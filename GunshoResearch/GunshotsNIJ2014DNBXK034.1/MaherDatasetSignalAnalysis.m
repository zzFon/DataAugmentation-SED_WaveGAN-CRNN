
figure(2);
clear all;
load('MB_sig239_357_shot01.mat');
file = MB_sig239_357_shot01;
fs = 50000;

i = 2;
s(i,:) = file(:,i);
% player = audioplayer(s(1,:),fs);
% player.play;

st = 3.03;
ed = 3.07;

subplot(2,3,1);plot(s(i,:));
subplot(2,3,2);plot(s(i,st*10^6:ed*10^6));

% ¾ùÖµÂË²¨
wnd = 100; % ½×Êý
b = (1/wnd)*ones(1,wnd);
a = 1;
sm = filter(b,a,s);

subplot(2,3,4);plot(sm(i,:));
subplot(2,3,5);plot(sm(i,st*10^6:ed*10^6));
axis([0,1.5*10^4,-5,5]);

y = s(i,st*10^6:ed*10^6);
p2 = abs(fft(y)/length(y)); 
y_fft = p2(1:length(y)/2+1);
y_fft(2:end-1) = 2*y_fft(2:end-1);
f = fs*(0:(length(y)/2))/length(y);
subplot(2,3,3);
plot(f,y_fft);

%subplot(2,3,6);
figure(1);
spectrogram(sm(i,st*10^6:ed*10^6),256,250,256,1e3,'yaxis');