import json
import shapely
from shapely import wkt

# step 1) create lists of roofs and grounds per city objects
def roof_boundaries(input_data):
    cityobjs = list(input_data['CityObjects'].keys())

    obj_roofs = {}
    roof_bounds = {}

    for i in cityobjs:
        if len(input_data['CityObjects'][i]['geometry']) == 0:
            continue
        else:
            type = input_data['CityObjects'][i]['geometry'][0]['type']
            boundaries = input_data['CityObjects'][i]['geometry'][0]['boundaries']
            smt_values = input_data['CityObjects'][i]['geometry'][0]['semantics']['values']
            smt_surfaces = input_data['CityObjects'][i]['geometry'][0]['semantics']['surfaces']

            roof_id = {}
            for id, surf in enumerate(smt_surfaces):
                if (surf['type'] == 'RoofSurface') or (surf['type'] == 'OuterFloorSurface'):
                    roof_id[id] = surf['id']

            obj_roofs[i] = list(roof_id.values())

            roof_val = {}
            for a in list(roof_id.keys()):
                vals = []
                if type == 'Solid':
                    for id, val in enumerate(smt_values[0]): # 0-0 / 1-1 / 2-2 / 3-2 / 4-3
                        if val == a:
                            vals.append(id)
                elif type == 'MultiSurface':
                    for id, val in enumerate(smt_values): # 0-0 / 1-1 / 2-2 / 3-2 / 4-3
                        if val == a:
                            vals.append(id)
                roof_val[roof_id[a]] = vals

            for a in list(roof_val.keys()):
                bounds = []
                for b in roof_val[a]:
                    if type == 'Solid':  # array depth == 4
                        bounds.append(boundaries[0][b])
                    elif (type == 'MultiSurface') or (type == 'CompositeSurface'):  # array depth == 3
                        bounds.append(boundaries[b])
                    else:
                        print(f'geometry type error : {type}')

                roof_bounds[a] = bounds

    return obj_roofs, roof_bounds


def ground_boundaries(input_data):
    cityobjs = list(input_data['CityObjects'].keys())

    obj_grounds = {}
    ground_bounds = {}

    for i in cityobjs:
        if len(input_data['CityObjects'][i]['geometry']) == 0:
            continue
        else:
            type = input_data['CityObjects'][i]['geometry'][0]['type']
            boundaries = input_data['CityObjects'][i]['geometry'][0]['boundaries']
            smt_values = input_data['CityObjects'][i]['geometry'][0]['semantics']['values']
            smt_surfaces = input_data['CityObjects'][i]['geometry'][0]['semantics']['surfaces']

            ground_id = {}
            for id, surf in enumerate(smt_surfaces):
                if surf['type'] == 'GroundSurface':
                    ground_id[id] = surf['id']

            obj_grounds[i] = list(ground_id.values())

            ground_val = {}
            for a in list(ground_id.keys()):
                vals = []
                if type == 'Solid':
                    for id, val in enumerate(smt_values[0]): # 0-0 / 1-1 / 2-2 / 3-2 / 4-3
                        if val == a:
                            vals.append(id)
                elif type == 'MultiSurface':
                    for id, val in enumerate(smt_values): # 0-0 / 1-1 / 2-2 / 3-2 / 4-3
                        if val == a:
                            vals.append(id)
                ground_val[ground_id[a]] = vals

            for a in list(ground_val.keys()):
                bounds = []
                for b in ground_val[a]:
                    if type == 'Solid':
                        bounds.append(boundaries[0][b])
                    elif type == 'MultiSurface':
                        bounds.append(boundaries[b])
                    else:
                        print(f'geometry type error : {type}')

                ground_bounds[a] = bounds

    return obj_grounds, ground_bounds

# step 2) get coordinates of vertices
def vertices_idx_to_coords(input_data):
    scale = input_data['transform']['scale']
    translate = input_data['transform']['translate']
    vertices = input_data['vertices']

    v_coords = {}
    for i in range(0, len(vertices)):
        vi = []
        vi_x = (vertices[i][0] * scale[0]) + translate[0]
        vi_y = (vertices[i][1] * scale[1]) + translate[1]
        #vi_z = (vertices[i][2] * scale[2]) + translate[2]

        vi.append(vi_x)
        vi.append(vi_y)
        #vi.append(vi_z)
        v_coords[i] = vi

    return v_coords

# step 3) get coordinates of boundaries
def boundary_idx_to_coords(input_dict, v_coords):
    bounds_coords = {}

    for uuid, bound in input_dict.items():
        bound_coords =[]
        for face in bound:
            face_coords = []
            for ring in face:
                ring_coords =[]
                for v in ring:
                    ring_coords.append(tuple(v_coords[v]))
                face_coords.append(ring_coords)
            bound_coords.append(face_coords)
        bounds_coords[uuid] = bound_coords

    return bounds_coords

def write_wkt_polygon(bounds_dict, output_f_name):
    bound_wkts = {}

    with open(output_f_name, 'w') as output:
        output.write('uuid; geom\n')

        for uuid, bound in bounds_dict.items():
            polygon_strs = []
            for face in bound:
                ring_strs = []
                for ring in face:
                    if ring[0] != ring[-1]:
                        ring.append(ring[0])
                    coords_list = []
                    for coord in ring:
                        coords_list.append(f'{coord[0]} {coord[1]}')
                    coords = ', '.join(coords_list)
                    ring_strs.append(f'({coords})')
                face_str = f'({', '.join(ring_strs)})'
                polygon_strs.append(face_str)

            if len(polygon_strs) == 1:
                wkt = f'POLYGON{polygon_strs[0]}'
            else:
                all_faces = ', '.join(polygon_strs)
                wkt = f'MULTIPOLYGON({all_faces})'

            output.write(f'{uuid}; {wkt}\n')
            bound_wkts[uuid] = wkt

    return bound_wkts


def cal_area(obj_surfs, surf_wkts, output_file_nm):
    obj_surf_union = {}
    obj_surf_area = {}

    with open(output_file_nm, 'w') as output:
        output.write('uuid; geom\n')

        for uuid, surfs in obj_surfs.items():
            if len(surfs) == 1:
                poly = wkt.loads(surf_wkts[surfs[0]])
                area = shapely.area(poly)

                obj_surf_union[uuid] = poly
                obj_surf_area[uuid] = area

                output.write(f'{uuid}; {poly}\n')

            elif len(surfs) > 1:
                polys = []
                for i in range(0, len(surfs)):
                    poly = wkt.loads(surf_wkts[surfs[i]])
                    polys.append(poly)

                union_polys = shapely.unary_union(polys)
                union_area = shapely.area(union_polys)

                obj_surf_union[uuid] = union_polys
                obj_surf_area[uuid] = union_area

                output.write(f'{uuid}; {union_polys}\n')

    return obj_surf_area


def diff_area(obj_roof_area, obj_ground_area):
    underpass_building_uuid = []
    only_roof_building_uuid = []

    for uuid, area in obj_roof_area.items():
        roof_area = area
        if uuid in obj_ground_area.keys():
            ground_area = obj_ground_area[uuid]

            diff = roof_area - ground_area  # roof - ground
            eps = 1e-8
            if diff > eps:
                underpass_building_uuid.append(uuid)
                underpass_building_uuid.append(diff)
        else:
            only_roof_building_uuid.append(uuid)

    return underpass_building_uuid, only_roof_building_uuid
