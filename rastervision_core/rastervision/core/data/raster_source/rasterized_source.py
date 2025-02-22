from typing import TYPE_CHECKING, List
import logging

from rasterio.features import rasterize
import numpy as np
import geopandas as gpd

from rastervision.core.data.raster_source import RasterSource

log = logging.getLogger(__name__)

if TYPE_CHECKING:
    from rastervision.core.box import Box
    from rastervision.core.data import VectorSource, RasterTransformer


def geoms_to_raster(df: gpd.GeoDataFrame, window: 'Box',
                    background_class_id: int, all_touched: bool,
                    extent: 'Box') -> np.ndarray:
    """Rasterize geometries that intersect with the window."""
    if len(df) == 0:
        return np.full(window.size, background_class_id, dtype=np.uint8)

    window_geom = window.to_shapely()

    # subset to shapes that intersect window
    df_int = df[df.intersects(window_geom)]
    # transform to window frame of reference
    shapes = df_int.translate(xoff=-window.xmin, yoff=-window.ymin)
    # class IDs of each shape
    class_ids = df_int['class_id']

    if len(shapes) > 0:
        raster = rasterize(
            shapes=list(zip(shapes, class_ids)),
            out_shape=window.size,
            fill=background_class_id,
            dtype=np.uint8,
            all_touched=all_touched)
    else:
        raster = np.full(window.size, background_class_id, dtype=np.uint8)

    return raster


class RasterizedSource(RasterSource):
    """A RasterSource based on the rasterization of a VectorSource."""

    def __init__(self,
                 vector_source: 'VectorSource',
                 background_class_id: int,
                 extent: 'Box',
                 all_touched: bool = False,
                 raster_transformers: List['RasterTransformer'] = []):
        """Constructor.

        Args:
            vector_source (VectorSource): The VectorSource to rasterize.
            background_class_id (int): The class_id to use for any background
                pixels, ie. pixels not covered by a polygon.
            extent (Box): Extent of corresponding imagery RasterSource.
            all_touched (bool, optional): If True, all pixels touched by
                geometries will be burned in. If false, only pixels whose
                center is within the polygon or that are selected by
                Bresenham's line algorithm will be burned in.
                (See rasterio.features.rasterize for more details). Defaults
                to False.
        """
        self.vector_source = vector_source
        self.background_class_id = background_class_id
        self.all_touched = all_touched

        self.df = self.vector_source.get_dataframe()
        self.validate_labels(self.df)

        super().__init__(
            channel_order=[0],
            num_channels_raw=1,
            raster_transformers=raster_transformers,
            extent=extent)

    @property
    def dtype(self) -> np.dtype:
        """Return the numpy.dtype of this scene"""
        return np.uint8

    @property
    def crs_transformer(self):
        return self.vector_source.crs_transformer

    def _get_chip(self, window):
        """Return the chip located in the window.

        Polygons falling within the window are rasterized using the class_id, and
        the background is filled with background_class_id. Also, any pixels in the
        window outside the extent are zero, which is the don't-care class for
        segmentation.

        Args:
            window: Box

        Returns:
            [height, width, channels] numpy array
        """
        log.debug(f'Rasterizing window: {window}')
        chip = geoms_to_raster(
            self.df,
            window,
            background_class_id=self.background_class_id,
            extent=self.extent,
            all_touched=self.all_touched)
        # Add third singleton dim since rasters must have >=1 channel.
        return np.expand_dims(chip, 2)

    def validate_labels(self, df: gpd.GeoDataFrame) -> None:
        geom_types = set(df.geom_type)
        if 'Point' in geom_types or 'LineString' in geom_types:
            raise ValueError('LineStrings and Points are not supported '
                             'in RasterizedSource. Use BufferTransformer '
                             'to buffer them into Polygons.')

        if len(df) > 0 and 'class_id' not in df.columns:
            raise ValueError('All label polygons must have a class_id.')
