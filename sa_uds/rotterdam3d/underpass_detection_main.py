import argparse
import sys
import json
import underpass_detection

def main():
    parser = argparse.ArgumentParser(description="Detect buildings with underpasses")

    parser.add_argument("inputfile", help="Input cityjson file (required)")

    args = parser.parse_args()

    try:
        with open(args.inputfile) as f:
            data = json.load(f)
    except Exception as e:
        print(e)
        sys.exit()

    obj_roofs, roof_bounds = underpass_detection.roof_boundaries(data)
    obj_grounds, ground_bounds = underpass_detection.ground_boundaries(data)

    v_coords = underpass_detection.vertices_idx_to_coords(data)

    roof_coords = underpass_detection.boundary_idx_to_coords(roof_bounds, v_coords)
    ground_coords = underpass_detection.boundary_idx_to_coords(ground_bounds, v_coords)

    ground_wkts = underpass_detection.write_wkt_polygon(ground_coords, 'ground_pre_union.wkt')
    roof_wkts = underpass_detection.write_wkt_polygon(roof_coords, 'roof_pre_union.wkt')

    obj_roof_area = underpass_detection.cal_area(obj_roofs, roof_wkts, 'roof_union.wkt')
    obj_ground_area = underpass_detection.cal_area(obj_grounds, ground_wkts, 'ground_union.wkt')

    underpass_building_uuid, only_roof_building_uuid = underpass_detection.diff_area(obj_roof_area, obj_ground_area)

    print(f'underpass_building_uuid\n{underpass_building_uuid}\n')
    print(f'only_roof_building_uuid\n{only_roof_building_uuid}')

if __name__ == "__main__":
    main()
