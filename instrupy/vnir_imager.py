
import uuid
import numpy as np
from instrupy.basic_sensor_model import BasicSensorModel
from instrupy.util import Maneuver, Orientation, SphericalGeometry, SyntheticDataConfiguration


class VNIRSensorModel(BasicSensorModel):
    def __init__(self, name=None, mass=None, volume=None, power=None,  orientation=None,
                 fieldOfViewGeometry=None, sceneFieldOfViewGeometry=None, maneuver=None, pointingOption=None, dataRate=None, syntheticDataConfig=None, bitsPerPixel=None, 
                 numberDetectorRows=None, numberDetectorCols=None, detectorWidth=None, focalLength=None, _id=None):
        super().__init__(name=name, mass=mass, volume=volume, power=power, orientation=orientation,
                         fieldOfViewGeometry=fieldOfViewGeometry, sceneFieldOfViewGeometry=sceneFieldOfViewGeometry, maneuver=maneuver, pointingOption=pointingOption, dataRate=dataRate, syntheticDataConfig=syntheticDataConfig, bitsPerPixel=bitsPerPixel,
                         numberDetectorRows=numberDetectorRows, numberDetectorCols=numberDetectorCols, _id=_id)
        self.detectorWidth = detectorWidth
        self.focalLength = focalLength

        self._type = "VNIR"

    # def __init__(self, focalLength, detectorWidth):
    #     self.detectorWidth = detectorWidth
    #     self.focalLength = focalLength
    
    def calc_data_metrics(self, sc_orbit_state, target_coords):
        obsv_metrics = super().calc_data_metrics(sc_orbit_state, target_coords)
        
        range_vec_norm_km = obsv_metrics["observation range [km]"]

        # Calculate FOV of a single detector, i.e. the IFOV (instantaneous FOV) as referred in texts.
        iFOV_deg = np.rad2deg(self.detectorWidth / self.focalLength)
        # Calculate the cross track spatial resolution of the ground-pixel
        res_CT_m = np.deg2rad(iFOV_deg)*range_vec_norm_km*1.0e3/np.cos(np.deg2rad(obsv_metrics['incidence angle [deg]']))
        # Calculate along-track spatial resolution of the ground-pixel
        res_AT_m = np.deg2rad(iFOV_deg)*range_vec_norm_km*1.0e3

        obsv_metrics["ground pixel along-track resolution [m]"] = round(res_AT_m, 2)
        obsv_metrics["ground pixel cross-track resolution [m]"] = round(res_CT_m, 2)    
        
        return obsv_metrics
    
    def __repr__(self):
        return "VNIRSensorModel.from_dict({})".format(self.to_dict())

    @staticmethod
    def from_dict(d):
        """ Parses a ``BasicSensorModel`` object from a normalized JSON dictionary. 
            Refer to :ref:`basic_sensor_model_desc` for description of the accepted key/value pairs.
        
        The following default values are assigned to the object instance parameters in case of 
        :class:`None` values or missing key/value pairs in the input dictionary.

        .. csv-table:: Default values
            :header: Parameter, Default Value
            :widths: 10,40

            orientation, Referenced and aligned to the SC_BODY_FIXED frame.
            fieldOfViewGeometry, CIRCULAR shape with 25 deg diameter.
            sceneFieldOfViewGeometry, fieldOfViewGeometry
            numberDetectorRows, 4
            numberDetectorRows, 4
            _id, random string
        
        :param d: Normalized JSON dictionary with the corresponding model specifications. 
        :paramtype d: dict

        :returns: ``BasicSensorModel`` object initialized with the input specifications.
        :rtype: :class:`instrupy.basic_sensor_model.BasicSensorModel`
            
        """
        instru_fov_geom = d.get("fieldOfViewGeometry", {'shape': 'CIRCULAR', 'diameter':25})  # default instrument FOV geometry is a 25 deg diameter circular shape
        scene_fov_geom = d.get("sceneFieldOfViewGeometry", instru_fov_geom)  # default sceneFOV geometry is the instrument FOV geometry
        default_orien = dict({"referenceFrame": "SC_BODY_FIXED", "convention": "REF_FRAME_ALIGNED"}) #  default orientation = referenced and aligned to the SC_BODY_FIXED frame.
        
        # parse the pointing options as a list of Orientation objects.
        pnt_opt_dict = d.get("pointingOption", None)
        _pointing_option = None
        if pnt_opt_dict:
            # translate to a list of Orientation objects
            if isinstance(pnt_opt_dict, list):
                _pointing_option = [Orientation.from_dict(x) for x in pnt_opt_dict]
            else:
                _pointing_option = [Orientation.from_dict(pnt_opt_dict)]
        
        return VNIRSensorModel(
                name = d.get("name", None),
                mass = d.get("mass", None),
                volume = d.get("volume", None),
                power = d.get("power", None),
                orientation = Orientation.from_json(d.get("orientation", default_orien)),
                fieldOfViewGeometry =  SphericalGeometry.from_json(instru_fov_geom),
                sceneFieldOfViewGeometry = SphericalGeometry.from_json(scene_fov_geom),
                maneuver =  Maneuver.from_json(d.get("maneuver", None)),
                dataRate = d.get("dataRate", None),
                bitsPerPixel = d.get("bitsPerPixel", None),
                syntheticDataConfig = SyntheticDataConfiguration.from_json(d.get("syntheticDataConfig", None)),
                numberDetectorRows = d.get("numberDetectorRows", 4),
                numberDetectorCols = d.get("numberDetectorCols", 4),
                detectorWidth = d.get("detectorWidth", 4),
                focalLength = d.get("focalLength", 4),
                pointingOption = _pointing_option,
                _id = d.get("@id", str(uuid.uuid4()))
                )