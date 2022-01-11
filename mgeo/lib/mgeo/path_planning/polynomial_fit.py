#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy as np
import matplotlib.pyplot as plt 

def noise(peak_to_peak):
    return peak_to_peak * (np.random.rand() - 0.5)


def add_noise(siganl, peak_to_peak):
    for i in range(len(siganl)):
        siganl[i] += noise(peak_to_peak)
    return siganl


def plot_dist(x, y):
    dist = []
    for i in range(len(x) - 1):
        dx = x[i+1] - x[i]
        dy = y[i+1] - y[i]
        dist.append(np.sqrt(dx**2 + dy**2))

    print('mean={:.2f}'.format(np.mean(dist)))

    plt.figure()
    plt.plot(dist,
        linestyle='',
        marker='o')
    plt.show()


def __creep(x, p, max_len, dx=0.1):
    total_len = 0

    x_now = x
    y_now = np.polyval(p, x_now)
    y_prev = y_now
    while total_len < max_len:
        
        # new point
        x_now += dx
        y_now = np.polyval(p, x_now)
        
        # distance 계산
        length = np.sqrt(dx**2 + (y_now - y_prev)**2)

        # 전체 length 업데이트
        total_len += length

        # y_prev 업데이트
        y_prev = y_now

    return x_now, y_now


def __get_polyfit_coeff_and_direction(x, y):
    # y = f(x) 방향으로 polyfit
    ret_x = np.polyfit(x, y, deg=3, full=True) 
    p_x = ret_x[0]
    residual_x = ret_x[1]

    # x = f(y) 방향으로 polyfit
    ret_y = np.polyfit(y, x, deg=3, full=True) 
    p_y = ret_y[0]
    residual_y = ret_y[1]

    res_threshold = 100

    if res_threshold < residual_y:
        # y = f(x) 방향으로 fit 해야 함
        ret = ret_x
        fitting_direction_x_to_y = True
    else:
        # x = f(y) 방향으로 fit 해야 함
        ret = ret_y
        fitting_direction_x_to_y = False
        
    p = ret[0]
    residual = ret[1]
    if residual > res_threshold:
        plt.figure()
        plt.plot(x, y,'r-o')
        if fitting_direction_x_to_y:
            plt.plot(x, np.polyval(p, x), 'b-x')
        else:
            plt.plot(np.polyval(p, y), y, 'b-x')
        plt.show()
        raise BaseException('[WARNING] res_threshold is over res_threshold. curve fitting may not be working correctly' )
    
    return p, fitting_direction_x_to_y


def __get_evenly_distributed_points_from_polyfit_result(x, y, 
    polyfit_coeff, interval, subsampling=1, creep_method=True, include_last_point=False):
    x_diff = x[-1] - x[0]

    # 우선 x가 증가하는 방향인지 감소하는 방향인지부터 파악
    if x[-1] - x[0] > 0:
        inc = True
    else:
        inc = False

    pd = np.polyder(polyfit_coeff) 

    # NOTE: 이 함수를 호출할 때 아무리 많아도 10000개 까지는 안 된다고 가정한다
    num_points_max = 100

    new_x = []
    new_y = []

    x_now = x[0]
    y_now = y[0]
    break_flag = False

    if creep_method:
        for i in range(num_points_max):
            if i == 0:
                new_x.append(x_now)
                new_y.append(y_now)

            # 다음 포인트를 찾은 것 
            if inc == True:
                dx = interval/(subsampling*10)
            else:
                dx = -interval/(subsampling*10)
            x_now, y_now = __creep(x_now, polyfit_coeff, interval, dx)

            # break 조건 체크
            if inc:
                # 증가하는 그래프라면, 다음 시점의 x가 끝값을 넘었을 때 종료
                if x_now > x[-1]:
                    # NOTE: 마지막 점 포함 안 시킬거면 그냥 break하면 됨
                    if include_last_point:
                        new_x.append(x[-1])
                        new_y.append(y[-1])
                    break
            else:
                # 감소하는 그래프라면, 다음 시점의 x가 끝값보다 작아졌을 때 종료
                if x_now < x[-1]:
                    # NOTE: 마지막 점 포함 안 시킬거면 그냥 break하면 됨
                    # 마지막 점 포함 시켜서 코드 한번 더 돌리려고 이럼
                    if include_last_point:
                        new_x.append(x[-1])
                        new_y.append(y[-1])
                    break

            new_x.append(x_now)
            new_y.append(y_now)

    else:
        for i in range(num_points_max * subsampling):
            if i % subsampling == 0:
                # 현재 시점에서의 y값을 계산하여 포함 시켜준다
                new_x.append(x_now)
                new_y.append(np.polyval(polyfit_coeff, x_now))

                fig = plt.figure()
                plt.plot(x, y, 
                    linestyle='--',
                    marker='o')
                plt.plot(x, np.polyval(polyfit_coeff, x),
                    linestyle='-',
                    marker='D')
                plt.plot(new_x, new_y,
                    linestyle='-',
                    marker='D',
                    color='r')
                fig.gca().axis('equal')
                plt.show()



            # 다음 시점의 x값을 계산한다
            dy_dx_now = np.polyval(pd, x_now)
            # 예를들어 dy_dx가 4이면, 현재 지점에서의 방향벡터가 (1,4)라는것
            # 우리가 원하는 건 대략 (1,4) 방향으로 interval만큼 갈 때
            # 다음 x의 좌표이므로,
            # 그만큼 진행하는 벡터는 interval/sqrt(1**2 + 4**2) * (1, 4) 가 되고
            # 여기서 x값만이 궁금한 것. 
            # 중요한 점은!!! dy_dx_now가 -값이면, del_move도 -방향으로 진행해야 하므로
            # del_move에 np.sign(dy_dx_now)를 반드시 곱해주어야 함

            del_move =  np.sign(dy_dx_now) * (interval/subsampling) / np.sqrt(1 + dy_dx_now**2)
            # print('x = {:.2f}, dy/dx = {:.2f}, del_move = {:.2f}'.format(x_now, dy_dx_now, del_move))
            x_now += del_move

            # break 조건 체크
            if inc:
                # 증가하는 그래프라면, 다음 시점의 x가 끝값을 넘었을 때 종료
                if x_now > x[-1]:
                    # NOTE: 마지막 점 포함 안 시킬거면 그냥 break하면 됨
                    if include_last_point:
                        new_x.append(x[-1])
                        new_y.append(y[-1])
                    break
            else:
                # 감소하는 그래프라면, 다음 시점의 x가 끝값보다 작아졌을 때 종료
                if x_now < x[-1]:
                    if include_last_point:
                        new_x.append(x[-1])
                        new_y.append(y[-1])
                    break

    return new_x, new_y


def get_evenly_distributed_points(x, y, interval, subsampling=1, unit_num=10, draw=False):
    total_x = []
    total_y = [] 

    num_loop = int(np.floor(len(x)/unit_num))
    
    if draw:
        fig = plt.figure()
        plt.plot(x, y, 
            linestyle='--',
            marker='o')
            

    end_flag = False
    start = 0
    while True:
        end = start + unit_num
        if end >= len(x) - 1:
            end_flag = True

            x_fit = x[start:]
            y_fit = y[start:]
            # if len(total_x) == 0:
            #     x_fit = x[start:]
            #     y_fit = y[start:]
            # else:
            #     x_fit = np.insert(x[start:], 0, total_x[-1])
            #     y_fit = np.insert(y[start:], 0, total_y[-1])
            include_last_point = True
            print('[DEBUG] Start={} End=(END)'.format(start))
        else:
            x_fit = x[start:end]
            y_fit = y[start:end]
            # if len(total_x) == 0:
            #     x_fit = x[start:end]
            #     y_fit = y[start:end]
            # else:
            #     x_fit = np.insert(x[start:end], 0, total_x[-1])
            #     y_fit = np.insert(y[start:end], 0, total_y[-1])
            include_last_point = False
            print('[DEBUG] Start={} End={}'.format(start,end))

        # 커브 피팅 방향이 어느 쪽이 적절한지를 
        # 양쪽 피팅을 다 해서 확인한다
        p, fitting_direction_x_to_y = __get_polyfit_coeff_and_direction(x_fit, y_fit)

        # 피팅 방향에 맞추어 새로운 포인트를 받는다    
        if fitting_direction_x_to_y:
            new_x, new_y = __get_evenly_distributed_points_from_polyfit_result(x=x_fit, y=y_fit, polyfit_coeff=p, 
                interval=interval, subsampling=subsampling, 
                creep_method=True, include_last_point=include_last_point)
            # new_x, new_y = __get_evenly_distributed_points_from_polyfit_result(
            #     x_fit, y_fit, p, interval, subsampling, include_last_point)
        else:
            new_y, new_x = __get_evenly_distributed_points_from_polyfit_result(
                x=y_fit, y=x_fit, polyfit_coeff=p,
                interval=interval, subsampling=subsampling,
                creep_method=True, include_last_point=include_last_point)

        total_x += new_x
        total_y += new_y

        if draw:
            plt.plot(x_fit, y_fit, 
                linestyle='--',
                marker='o')
            plt.plot(new_x, new_y,
                linestyle='-',
                marker='D')

        start += unit_num - 1
        if end_flag:
            break

    # 디버깅용으로 Plot
    if draw:
        # fig = plt.figure()
        # plt.plot(x, y, 
        #     linestyle='--',
        #     marker='o')
        # plt.plot(total_x, total_y,
        #     linestyle='-',
        #     marker='D')
        fig.gca().axis('equal')
        plt.show()

    return total_x, total_y


def test_case1():

    """ Case1 """
    def org_func(x):
        return 0.02 * x**3 - 0.1 * x**2 + 2 * x - 10 

    size = 10
    x = np.arange(0, size)
    y = org_func(x)
    y = add_noise(y, 5)
    new_x, new_y = get_evenly_distributed_points(x, y, interval=1.5, subsampling=10, draw=True)
    plot_dist(new_x, new_y)


def test_case2():
    """ Case2 """
    size = 10
    x = np.array([1,1,1,1,1,1,1,1,1,1])
    x = add_noise(x, 0.5)
    y = np.array([0,1,2,3,4,5,6,7,8,9])
    new_x, new_y = get_evenly_distributed_points(x, y, interval=0.3, subsampling=10, draw=True)
    plot_dist(new_x, new_y)


def test_case3():
    """ Case 3"""
    x = np.arange(0, 10)
    y = -0.1 * x + 3
    y = add_noise(y, 0.2)
    new_x, new_y = get_evenly_distributed_points(x, y, interval=2, subsampling=10, draw=True)
    plot_dist(new_x, new_y)


def test_case4():
    """ Case 4 """
    # def another_func(x):
    #     return  -0.05 * x**2 - 0.1 * x + 5

    def another_func(x):
        return  3 * x**2 + 5

    x = np.array([-5, -3, -2, 0, 1, 2, 4, 6])
    y = another_func(x)
    new_x, new_y = get_evenly_distributed_points(x, y, interval=2, subsampling=10, draw=True)
    plot_dist(new_x, new_y)


def test_case5():
    """ Case1 """
    # def org_func(x):
    #     return 0.02 * x**3 - 0.1 * x**2 + 2 * x - 10 

    def org_func(x):
        
        return 2 * x - 10

    size = 50
    x = np.arange(0, size)
    y = org_func(x)
    y = add_noise(y, 5)
    new_x, new_y = get_evenly_distributed_points(x, y,
        interval=1.5, subsampling=10, unit_num=10, draw=True)
    plot_dist(new_x, new_y)
    

if __name__ == '__main__':    
    test_case1()
    test_case2()
    test_case3()
    test_case4()
    test_case5()