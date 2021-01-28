
figure;clear all;
load('MB_sig239_357_shot10.mat');
file = MB_sig239_357_shot10;
fs = 50000;

s(1,:) = file(:,1);
% player = audioplayer(s(1,:),fs);
% player.play;

st = 1.78;
ed = 1.82;

subplot(2,2,1);plot(s(1,:));
subplot(2,2,2);plot(s(1,st*10^6:ed*10^6));

% ¾ùÖµÂË²¨
wnd = 100; % ½×Êý
b = (1/wnd)*ones(1,wnd);
a = 1;
sm = filter(b,a,s);

subplot(2,2,3);plot(sm(1,:));
subplot(2,2,4);plot(sm(1,st*10^6:ed*10^6));