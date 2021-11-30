function [grad_W, grad_b] = ComputeGradient_2nd(H, Y, P, W, lambda)

%G = zeros(size(Y));
G = -(Y - P)';
%grad_L_W = zeros(size(G,1),size(X,1));
%grad_L_b = zeros(size(W,1),1);

grad_L_W = 1/size(H,2) * G' * H';
grad_L_b = 1/size(H,2) * G' * ones(size(H,2),1);

%grad_W = zeros(size(G,1),size(X,1));
grad_W = grad_L_W + 2*lambda.*W;
%grad_b = zeros(size(W,1),1);
grad_b = grad_L_b;