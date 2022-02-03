import os
import sys
current_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(current_path)
sys.path.append(os.path.normpath(os.path.join(current_path, '../')))

import vtk
from lib.common import display, file_io, vtk_utils

# NOTE: testing applicability of gmsh
# import gmsh

def make_road(py_vertices, py_faces, debug_print=False):
    """
    도로의 3D 형상에 해당하는 vtkPolyData 타입의 데이터를 만들어 반환한다.
    :return: 도로의 3D 형상에 해당하는 vtkPolyData 타입 데이터
    """

    # 도로의 3D 형상을 정의하기 위한 점과 면의 리스트를 생성한다.
    #py_vertices = _make_vertices()
    #py_faces = _make_faces()

    # 최종적으로는 아래 vtkPolyData 타입의 road 변수를 만들어 반환할 것이다.
    road = vtk.vtkPolyData()

    # 위 road 변수를 만들기 위해 다음 타입의 변수들을 먼저 만들어야 한다.
    vtk_vertices = vtk.vtkPoints()  # 점 정보
    vtk_faces = vtk.vtkCellArray()  # 면 정보
    vtk_scalars = vtk.vtkFloatArray()  # 각 점에 스칼라값을 할당할 수 있는데, 그 정보를 담는 객체이다.
    # [참고] vtk_scalars 변수는 여기서는 필요한 것은 아니긴 함. 참고용으로 넣어둠.

    # 1) vtkPoint 타입의 변수를 만든다.
    if debug_print:
        print('\n-------- make vtk_vertices --------')
    for i, xi in enumerate(py_vertices):
        #print('  i = {}, xi = {}'.format(i, xi))
        # vtk_vertices.InsertPoint(i, xi)
        vtk_vertices.InsertNextPoint(xi)

    # 2) vtkCellArray 타입의 변수를 만든다.
    if debug_print:
        print('\n-------- make vtk_faces --------')
    for pt in py_faces:
        #print('  pt = {}'.format(pt))

        # tuple을 바로 넣을 수 없고, vtkIdList 타입을 만들어서 이를 전달해야
        # vtkCellArray 타입의 객체를 초기화할 수 있다
        vil = vtk_utils.convert_to_vtkIdList(pt)
        #print('  vil = [{0}, {1}, {2}, {3}] (vtkIdList Type)'.format(vil.GetId(0), vil.GetId(1), vil.GetId(2), vil.GetId(3)))

        vtk_faces.InsertNextCell(vil)

    # 3) vtkFloatArray 타입의 변수를 만든다.
    if debug_print:
        print('\n-------- make vtk_scalars --------')
    for i, _ in enumerate(py_vertices):
        if debug_print:
            print('  CALL: vtk_scalars.InsertTuple1({0}, {0})'.format(i))
        vtk_scalars.InsertTuple1(i, i)

    # 1) 만들어진 vtkPoint 타입 변수를 출력해본다.
    if debug_print:
        print('\n-------- Vertices (arg: vtk_vertices, type: vtkPoints) --------')
        for i in range(0, vtk_vertices.GetNumberOfPoints()):
            print('  vtk_vertices.GetPoint({}) = {}'.format(i, vtk_vertices.GetPoint(i)))

    # 2) 만들어진 vtkCellArray 타입 변수를 출력해본다.
    # vtkCellArray 타입의 인스턴스인 polys는 각 면을 구성하는 꼭지점에 대한 index를 담고있다.
    if debug_print:
        print('\n-------- Faces (arg: vtk_faces,  type: vtkCellArray) --------')
        # for i in range(0, vtk_faces.GetNumberOfCells()):
        #     print('  cells.GetCell({}) = {}'.format(i, vtk_faces.GetCell(i)))

    # vtkCellArray를 이렇게 받아오면 되나?
    # syntax: V.GetNextCell(vtkIdList) -> int
    # first DO
    num_call = 0
    idList = vtk.vtkIdList()
    ret = vtk_faces.GetNextCell(idList)
    if debug_print:
        if ret == 0:
            print('[ERROR] ret = vtk_faces.GetNextCell(idList) returned 0! at num_call = {0}'.format(num_call))
        else:
            print('  vtk_faces.GetNextCell(idList): num_call = {} -> [{}, {}, {}, {}]'.format(
                num_call, idList.GetId(0), idList.GetId(1), idList.GetId(2), idList.GetId(3)))

    # next, while
    while ret == 1:
        num_call = num_call + 1
        idList = vtk.vtkIdList()
        ret = vtk_faces.GetNextCell(idList)
        if debug_print:
            if ret == 0:
                print('  vtk_faces.GetNextCell(idList): num_call = {} -> Reached the end of the cell array.'.format(num_call))
                break
            else:
                print('  vtk_faces.GetNextCell(idList): num_call = {} -> [{}, {}, {}, {}]'.format(
                    num_call, idList.GetId(0), idList.GetId(1), idList.GetId(2), idList.GetId(3)))

    # 3) 만들어진 vtkFloatArray 타입 변수를 출력해본다
    if debug_print:
        print('\n-------- Scalar Value (arg: vtk_scalars, type: vtkFloatArray) --------')
        for i in range(0, vtk_scalars.GetNumberOfValues()):
            print('  vtk_scalars.GetValue({}) = {}'.format(i, vtk_scalars.GetValue(i)))

    # 앞서 만든 vtkPoint, vtkCellArray, vtkFloatArray 타입 변수를 이용하여
    # 3D 모델에 해당하는 road 변수(vtkPolyData 타입)의 값들을 설정해준다
    road.SetPoints(vtk_vertices)
    road.SetPolys(vtk_faces)
    road.GetPointData().SetScalars(vtk_scalars)

    return road


def make_road_delaunay(py_vertices, py_faces, tolerance, print_log=False):
    '''
    Use vtkDelaunay2D to create a road mesh
    input 1: list of all vertices (x,y,z coordinates) selected as planes
    input 2: list of all face vertices selected
    output: vtkDelaunay object

    The notes for methods #1, 2, and 3 are intended
    to be interchangable
    https://vtk.org/doc/nightly/html/classvtkDelaunay2D.html
    '''
    if print_log is True:
        for i, vertex in enumerate(py_vertices):
            print(i, vertex)
        for point_set in py_faces:
            for point in point_set:
                print(point)

    boundary_vertices = vtk.vtkPoints()
    boundary_faces = vtk.vtkCellArray()

    for vertex in py_vertices:
        boundary_vertices.InsertNextPoint(vertex)

    # NOTE: Method 1: vtkPolygon() -> vtkCellArray
    # for point_set in py_faces:
    #     boundary = vtk.vtkPolygon()
    #     for point in point_set:
    #         boundary.GetPointIds().InsertNextId(int(point))
    #     # boundary.GetPointIds().InsertNextId(point_set[0])
    #     boundary_faces.InsertNextCell(boundary)

    # NOTE: Method 2: directly insert cells into vtkCellArray
    for point_set in py_faces:
        boundary_faces.InsertNextCell(len(point_set))
        for point in point_set:
            boundary_faces.InsertCellPoint(point)

    # NOTE: Method 3: use SetLines() to create the constrained plane
    # nothing here yet

    poly_profile = vtk.vtkPolyData()
    poly_profile.SetPoints(boundary_vertices)
    poly_profile.SetPolys(boundary_faces)

    delny = vtk.vtkDelaunay2D()
    delny.SetInputData(poly_profile)
    delny.SetSourceData(poly_profile)
    delny.SetTolerance(tolerance)
    # delny.SetOffset(2.)
    
    delny.Update()

    return delny.GetOutput()


def make_road_gmsh(py_vertices, py_faces, savefile_name):
    '''
    Use Gmsh to generate the road mesh
    input 1: list of all vertices selected as planes
    input 2: list of all face vertices selected
    output: direct file output of .msh file
    '''
    pass
    # model = gmsh.model
    # factory = model.geo
    
    # gmsh.initialize()
    # # gmsh.option.setNumber('General.Terminal', 1)
    # model.add('road')

    # lc = 1 # characteristic length

    # curveloop_list = list()
    # index_offset = 1

    # for idx, pt in enumerate(py_vertices):
    #     factory.addPoint(pt[0], pt[1], pt[2], lc, idx+index_offset)
    #     # factory.addPoint(pt[0], pt[1], 0, lc, idx+index_offset) # this works well
    #     # factory.addPoint(pt[0]*0.1, pt[1]*0.1, pt[2]*0.01, lc, idx+index_offset)

    # for idx, point_set in enumerate(py_faces):
    #     for index in range(len(point_set)):
    #         # assume py_faces is closed always
    #         if index == len(point_set)-index_offset:
    #             factory.addLine(point_set[index]+index_offset, point_set[0]+index_offset,
    #             index+index_offset)
    #         else:
    #             factory.addLine(point_set[index]+index_offset, point_set[index+1]+index_offset,
    #             index+index_offset)

    #         curveloop_list.append(index+index_offset)
        
    #     factory.addCurveLoop(curveloop_list, idx+index_offset)
    #     curveloop_list = list()

    #     factory.addPlaneSurface([idx+index_offset], idx+index_offset)

    # factory.synchronize()

    # # change mesh properties
    # # gmsh.option.setNumber("Mesh.CharacteristicLengthExtendFromBoundary", 0)
    # # gmsh.option.setNumber("Mesh.CharacteristicLengthFromCurvature", 0)
    
    # gmsh.option.setNumber("Mesh.CharacteristicLengthFactor", 1)
    # # gmsh.option.setNumber("Mesh.CharacteristicLengthMin", 1)

    # # set 2D meshing algorithm to delaunay
    # gmsh.option.setNumber('Mesh.Algorithm', 5) # 5 = delaunay
    # # gmsh.option.setNumber('Mesh.RecombineAll', 1) # enable 2D recombine

    # model.mesh.generate(2)

    # gmsh.write(savefile_name)

    # gmsh.fltk.run()
    # gmsh.finalize()


def plot_vtkPolyData(poly_obj, color=''):
    colors = vtk.vtkNamedColors()

    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(poly_obj)
    mapper.ScalarVisibilityOff()


    actor = vtk.vtkActor()
    actor.SetMapper(mapper)
        
    if color != '':
        actor.GetProperty().SetColor(colors.GetColor3d(color))

    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    # Create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Assign actor to the renderer
    ren.AddActor(actor)

    # Enable user interface interactor
    iren.Initialize()
    renWin.Render()
    iren.Start() # 이걸 주석 해제하면 보여주는 창이 뜬다


def smooth_mesh(polydata_in):
    '''
    Smoothes the mesh polygon using the Laplacian smoothing equation
    input: polydata object
    output: smoothed polydata object
    https://vtk.org/doc/nightly/html/classvtkSmoothPolyDataFilter.html
    '''
    smoother = vtk.vtkSmoothPolyDataFilter()
    smoother.SetInputData(polydata_in)
    smoother.SetNumberOfIterations(30)

    smoother.Update()

    return smoother.GetOutput()


def unify_normal(polydata_in):
    '''
    uses the normal generation algorithm to determine the normals of each polygon data
    input: polydata object
    output: a new normal calculated polydata object
    https://vtk.org/doc/nightly/html/classvtkPolyDataNormals.html
    '''
    normals = vtk.vtkPolyDataNormals()
    normals.SetInputData(polydata_in)
    normals.ComputeCellNormalsOn()

    normals.Update()

    polydata_out = vtk.vtkPolyData()
    polydata_out.DeepCopy(normals.GetOutput())

    return polydata_out

def write_obj(poly_obj, output_file_prefix, preview=False):
    """
    3D 형상을 입력하여 obj 파일을 만든다.
    :param poly_obj: 출력할 3D 형상 (vtkPolyData 타입)
    :param output_file_prefix: 출력할 파일 이름 (단, 확장자는 붙이면 안 된다)
    """
    obj_file_prefix = output_file_prefix

    # Draw Before OBJ Write
    # Now we'll look at it.
    mapper = vtk.vtkPolyDataMapper()
    if vtk.VTK_MAJOR_VERSION <= 5:
        mapper.SetInput(poly_obj)
    else:
        # NOTE: 임시 시험용으로 SetInputConnection으로 대체
        mapper.SetInputData(poly_obj)
        # mapper.SetInputConnection(poly_obj.GetOutputPort())
    actor = vtk.vtkActor()
    actor.GetProperty().SetRepresentationToWireframe()
    actor.SetMapper(mapper)

    # Create a rendering window and renderer
    ren = vtk.vtkRenderer()
    renWin = vtk.vtkRenderWindow()
    renWin.AddRenderer(ren)

    # Create a renderwindowinteractor
    iren = vtk.vtkRenderWindowInteractor()
    iren.SetRenderWindow(renWin)

    # Assign actor to the renderer
    ren.AddActor(actor)

    # Enable user interface interactor
    iren.Initialize()
    renWin.Render()
    
    if preview:
        iren.Start()

    # OBJ Write
    objExporter = vtk.vtkOBJExporter()
    objExporter.SetFilePrefix(obj_file_prefix)
    objExporter.SetRenderWindow(renWin)
    objExporter.Write()