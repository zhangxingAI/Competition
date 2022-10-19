clc;
clear;
close all;
%%
%初始条件
count_num = 10000;
x0 = 0;
y0 = 3.95;
x1 = -50;
y1 = 0.05;
x00 = 0;
for iii = 1:100
y00 = 3.95 + iii * 0.01;
x01 = 0;
y01 = 0;
dt = 0.1;
J = [1,0];
disp_min = sqrt((x0 - x1)^2 + (y0 - y1)^2);
%%
P = [x0,y0];
P1 = [x0,-y0];
E = [x1,y1];
PP = [x00,y00];
S_ini = [(x00 + x0) / 2 - x1,(y00 + y0) / 2 - y1];
ve = 0.25 * norm_1(S_ini);
E = E + ve * dt;        %E点坐标
S = E - P;              %两点距离
vp = 0.2 * norm_1(S + ve * dt);%p速度
P = P + vp * dt;        %P点坐标
for i = 1:count_num
    ex(i) = E(1);
    ey(i) = E(2);
    px(i) = P(1);
    py(i) = P(2);
    disp = sqrt(S(1)^2 + S(2)^2);
    logc = escape(E,P,PP);
    if disp < 0.4 
        get = 1;
        break
    end
    if i >= 3600
        get = 1;
        break
    end
    if E(2) >= y00
        get = 1;
        break
    elseif E(1)>= 0
        get = 0;
        break
    end
    if logc ~= [0,0]
        ve_temp = 0.25 * norm_1(logc);%e速度
    else
        t_rem = 360 - dt * i;
        t_least = abs(E(1) / ve(1));
        if t_least < t_rem
            get = 0;
        else
            get = 1;
        end
        break
    end
    ve = ve_temp;        %E点坐标
    E = E + ve * dt;
    S = E - P;              %两点距离
    vp_temp = 0.2 * norm_1(S + ve);   %p速度
    theta_2 = get_direc(P,E,vp_temp) * acos((vp * vp_temp') / (sqrt(vp(1)^2 + vp(2)^2) * sqrt(vp_temp(1)^2 + vp_temp(2)^2)));        %P偏转角
    if abs(theta_2) > asin(dt/5)
        theta_2 = asin(dt/5) * theta_2 / abs(theta_2);
    end
    vp = rotate_1(vp,theta_2);        %P点坐标
    P = P + vp * dt;
end
get1(iii) = get;
end
%%
% plot(ex,ey,px,py);
% axis equal
% circle(E,P);
%%
function [] = circle(e,p)
x0 = p(1);
y0 = p(2);
x1 = e(1);
y1 = e(2);
dist = sqrt((x1-x0)^2+(y1-y0)^2);%距离
t1 = dist/9;
r = 20 * t1;%圆半径
h = 25/9;
x2 = x1 + h * (x0 - x1);%圆心坐标
y2 = y1 + h * (y0 - y1);%圆心坐标
rectangle('Position',[x2-r,y2-r,2*r,2*r],'Curvature',[1,1],'linewidth',1),axis equal
end
function y = norm_1(x)
a = x(1);
b = x(2);
val = sqrt(a^2 + b^2);
y = x / val;
end
function y = get_direc(e,p,n)
ya = n(2) / n(1) * (p(1) - e(1)) + e(2) - p(2);
if ya ~= 0
    y = ya / abs(ya);
else
    y = ya;
end
end
function y = rotate_1(a,n)
T = [cos(n),sin(n);-sin(n),cos(n)];
A = T * a';
y = [A(1),A(2)];
end
function y = escape(e,p,pp)
x0 = p(1);
y0 = p(2);
x1 = e(1);
y1 = e(2);
point = pp;
dist = sqrt((x1-x0)^2+(y1-y0)^2);%距离
t1 = dist/9;
r = 20 * t1;%圆半径
h = 25/9;
x2 = x1 + h * (x0 - x1);%圆心坐标
y2 = y1 + h * (y0 - y1);%圆心坐标
x2p = (x1 + x2) / 2;%圆心坐标1
y2p = (y1 + y2) / 2;%圆心坐标1
R = 12.5 * t1;
a = x2 - x2p;
b = y2 - y2p;
c = (x2^2 - x2p^2 + y2^2 - y2p^2 + R^2 - r^2) / 2;
a1 = b^2 / a^2 + 1;
b1 = -2*b*c/a^2 + 2*b*x2/a - 2*y2;
c1 = c^2/a^2 + x2^2 - 2*c*x2/a + y2^2 - r^2;
y3 = (-b1+sqrt(b1^2-4*a1*c1))/(2*a1);%切点坐标
y4 = (-b1-sqrt(b1^2-4*a1*c1))/(2*a1);%切点坐标
x3 = (c-b*y3)/a;
x4 = (c-b*y4)/a;
yk1 = y3 - (y3 - y1)/(x3 - x1) * x3;%切线与y轴交点
if yk1 < point(2)
    y = [0,0];%逃离
else
    y = [x0 - x1,(y0 + point(2))/2 - y1];%沿中点运动
end
end
function y = escape_1(e,p,p1)
x0 = p(1);
y0 = p(2);
x01 = p1(1);
y01 = p1(2);
x1 = e(1);
y1 = e(2);
dist = sqrt((x1-x0)^2+(y1-y0)^2);%距离
t1 = dist/9;
r = 20 * t1;%圆半径
h = 25/9;
x2 = x1 + h * (x0 - x1);%圆心坐标
y2 = y1 + h * (y0 - y1);%圆心坐标
x2p = (x1 + x2) / 2;%圆心坐标1
y2p = (y1 + y2) / 2;%圆心坐标1
R = 12.5 * t1;
a = x2 - x2p;
b = y2 - y2p;
c = (x2^2 - x2p^2 + y2^2 - y2p^2 + R^2 - r^2) / 2;
a1 = b^2 / a^2 + 1;
b1 = -2*b*c/a^2 + 2*b*x2/a - 2*y2;
c1 = c^2/a^2 + x2^2 - 2*c*x2/a + y2^2 - r^2;
y3 = (-b1+sqrt(b1^2-4*a1*c1))/(2*a1);%切点坐标
y4 = (-b1-sqrt(b1^2-4*a1*c1))/(2*a1);%切点坐标
x3 = (c-b*y3)/a;
x4 = (c-b*y4)/a;
yk1 = y4 - (y4 - y1)/(x4 - x1) * x4;%切线与y轴交点
%%
dist = sqrt((x1-x01)^2+(y1-y01)^2);%距离
t1 = dist/9;
r = 20 * t1;%圆半径
h = 25/9;
x2 = x1 + h * (x01 - x1);%圆心坐标
y2 = y1 + h * (y01 - y1);%圆心坐标
x2p = (x1 + x2) / 2;%圆心坐标1
y2p = (y1 + y2) / 2;%圆心坐标1
R = 12.5 * t1;
a = x2 - x2p;
b = y2 - y2p;
c = (x2^2 - x2p^2 + y2^2 - y2p^2 + R^2 - r^2) / 2;
a1 = b^2 / a^2 + 1;
b1 = -2*b*c/a^2 + 2*b*x2/a - 2*y2;
c1 = c^2/a^2 + x2^2 - 2*c*x2/a + y2^2 - r^2;
y3 = (-b1+sqrt(b1^2-4*a1*c1))/(2*a1);%切点坐标
y4 = (-b1-sqrt(b1^2-4*a1*c1))/(2*a1);%切点坐标
x3 = (c-b*y3)/a;
x4 = (c-b*y4)/a;
yk2 = y3 - (y3 - y1)/(x3 - x1) * x3;%切线与y轴交点
if yk1 > yk2
    y = [0,0];%逃离
else
    y = [(x0 + x01)/2 - x1,(y0 + y01)/2 - y1];%沿中点运动
end
end