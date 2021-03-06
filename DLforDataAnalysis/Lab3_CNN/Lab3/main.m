load('X');

Convmain = ConvNet();
Convmain.eta = 0.001;
Convmain.rho = 0.9;
epoch = 3;
batch = 100;

%the number of filters applied at layer 1: n1
%the width of the filters applied at layer 1: k1
%(Remember the filter applied will have size d × k1.)
%the number of filters applied at layer 2: n2
%the width of the filters applied at layer 2: k2
%(Remember the filter applied will have size n1 × k2.)

%congifuration
k1=5; n1=20;
k2=3; n2=20;
K=18;
%sig1 = sqrt(2/d/k1/n1); %sparse matrix => need to fix !!
sig1 = sqrt(2/k1/d/n1); %sparse matrix => need to fix !!
sig2 = sqrt(2/n1/k2/n2); %He Init
F1 = randn(d, k1, n1)*sig1;
F2 = randn(n1, k2, n2)*sig2;

Convmain.F1 = F1;
Convmain.F2 = F2;

%Convmain.MFs{1} = MakeMFMatrix(Convmain.F{1},n_len);
n_len1 = n_len-k1+1;
%Convmain.MFs{2} = MakeMFMatrix(Convmain.F{2},n_len1);
n_len2 = n_len1 -k2 +1;
fsize=n2*n_len2;

sig3 = sqrt(2/K/fsize);
W = randn(K, fsize)*sig3;
Convmain.W = W;

[d, k1, nf] = size(Convmain.F1);

%MX = MakeMXMatrix(X, d, k1, nf);
%s1 = MX * Convmain.F{1}(:);
%s2 = MFs{1} * X;

n_c = zeros(K,1);

Y = zeros(K,size(ys,1));

for i = 1:size(Y,2)
    Y(ys(i,1),i)=1;
    n_c(ys(i,1),1) = n_c(ys(i,1),1) + 1;
end

%X_valid = X_bal(:,:200);
%Y_valid = Y_bal(:,:200);
%X_train = X_bal(:,201:);
%Y_train = Y_bal(:,201:);

min_class = min(n_c);

n=size(X,2);

moment_W = zeros(size(W));
moment_F2 = zeros(size(F2));
moment_F1 = zeros(size(F1));
dLdW = 0;
dldvecF_1 = 0;
dldvecF_2 = 0;
train_loss = [];
train_acc = [];
vaild_loss = [];
valid_acc = [];

%profile on

for i = 1:epoch
    temp = randperm(n);
    X = X(:,temp);
    Y = Y(:,temp);

    [X_bal,Y_bal] = MakeCompen(X,Y,K,min_class);

    n_bal = size(X_bal,2);
    for a = 1:n_bal/batch
        X_batch = X_bal(:,(a-1)*batch+1:a*batch);
        Y_batch = Y_bal(:,(a-1)*batch+1:a*batch);
        MF1 = MakeMFMatrix(Convmain.F1, n_len);
        MF2 = MakeMFMatrix(Convmain.F2, n_len1);
        %[Convmain,loss] = Convmain.ComputeLoss(X_batch,Y_batch,MF1,MF2);

        G_batch = -(Y_batch - Convmain.P_batch);
        dLdW = 1/batch * G_batch * Convmain.X_batch_2';
        
        %%%%%%%%%%%%%
        moment_W = rho*moment_W + eta*dLdW;
        Convmain.W = Convmain.W - moment_W;

        %%%%%%%%%%%%
        %Convmain.W = Convmain.W - eta*dLdW;
        G_batch = Convmain.W'*G_batch;
        G_batch = G_batch.*Ind(Convmain.X_batch_2);
        for j = 1:batch
            x_j = Convmain.X_batch_1(:,j);
            g_j = G_batch(:,j);
            v = g_j' * MakeMXMatrix(x_j,size(F2,1),k2,n2);
            %{
            %%%%%%%%%%%%%%%sparse version
            M = MakeMFMatrix_improved(x_j, size(F2,1), k2);
            g_matrix = zeros(n_len2,n2);
            for t=1:n_len2
                g_matrix(t,:) = g_j((t-1)*n2+1 : t*n2,1)';
            end
            v = M' * g_matrix;
            %%%%%%%%%%%%%%%%
            %}
            dldvecF_2 = dldvecF_2 + 1/batch*v;
            dldF_2 = reshape(dldvecF_2,[n1,k2,n2]);%how reshape? sus!!!!!
            %%%%%%%%%%%%%%%%
            moment_F2 = rho*moment_F2 + eta*dldF_2;
            Convmain.F2 = Convmain.F2 - moment_F2;
            %%%%%%%%%%%%%%
            %Convmain.F2 = Convmain.F2 - eta*dldF_2;
        end
        
        MF2 = MakeMFMatrix(Convmain.F2,n_len1);
        G_batch = MF2' *  G_batch;
        G_batch = G_batch .* Ind(Convmain.X_batch_1);
        for j = 1:batch
            g_j = G_batch(:,j);
            x_j = X_batch(:,j);
            v = g_j' * MakeMXMatrix(x_j,size(F1,1),k1,n1);
            %%%%%%%%%%%%%%%%%
            %sparsed = sparse(MakeMXMatrix(x_j,size(F1,1),k1,n1));
            %v = g_j' * sparsed; %sparse version
            %%%%%%%%%%%%%%%%%
            dldvecF_1 = dldvecF_1 + 1/batch*v;
            dldF_1 = reshape(dldvecF_1,[d,k1,n1]);
            %%%%%%%%%%%%%%%%%
            moment_F1 = rho*moment_F1 + eta*dldF_1;
            Convmain.F1 = Convmain.F1 - moment_F1;
            %%%%%%%%%%%%%%%%
            %Convmain.F1 = Convmain.F1 - eta*dldF_1;
        end
        MF1 = MakeMFMatrix(Convmain.F1, n_len);
        train_loss = cat(2,train_loss,Convmain.ComputeLoss(X,Y,MF1,MF2));
        %train_acc = cat(2,train_loss,ComputeAccuracy(X,Y,Convmain,n_len,n_len1));
        %vaild_loss = [];
        %valid_acc = [];
        %Convmain.MF1 = MakeMFMatrix(Convmain.F{1},n_len); %it;s updated in
        %the beginning of for loop
        %Gs = NumericalGradient(X_batch, Y_batch, Convmain, 1e-6);
        
    end
end
%profile viewer

acc = ComputeAccuracy(X, Y, Convmain,n_len,n_len1)






    