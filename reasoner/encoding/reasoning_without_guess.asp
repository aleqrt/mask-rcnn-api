%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%intersections along vertical axis or horizontal axis
inLevelNet(C1, ID1, C2, ID2, horizontal) :-     net(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                net(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Ys1 <= Yd2, Yd1 >= Ys2.

inLevelNet(C1, ID1, C2, ID2, vertical) :-     net(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                net(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Xs1 <= Xd2, Xd1 >= Xs2.
                                                
                                                
inLevelCad(C1, ID1, C2, ID2, horizontal) :-     cad(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                cad(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Ys1 <= Yd2, Yd1 >= Ys2.
                                                
                                                
inLevelCad(C1, ID1, C2, ID2, vertical) :-     cad(C1, ID1, Xs1, Ys1, Xd1, Yd1),
                                                cad(C2, ID2, Xs2, Ys2, Xd2, Yd2),
                                                ID1 <> ID2,
                                                Xs1 <= Xd2, Xd1 >= Xs2.                                                
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%count instances of each component in cad and in net and then compare

component(X):- cad(X, _, _, _, _, _).
component(X):- net(X, _, _, _, _, _).


numInstancesCad(X,N):- component(X), #count{Id: cad(X, Id, _, _, _, _)}=N.

numInstancesNet(X,N):- component(X), #count{Id: net(X, Id, _, _, _, _)}=N.


problem(X,N_CAD,N_NET):- numInstancesCad(X,N_CAD), numInstancesNet(X,N_NET), N=N_CAD-N_NET, N!=0.
absentComponent(X,N):- numInstancesCad(X,N_CAD), numInstancesNet(X,N_NET), N=N_CAD-N_NET, N>0.


inExcessComponent(X,N):- numInstancesCad(X,N_CAD), numInstancesNet(X,N_NET), N=N_NET-N_CAD, N>0.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%relation graph representation

intersectionPercentage(50).
distancePercentage(20).



%calcolo la dimensione di ogni componente
componentDimensionCad(ID1,Width,Lenght):- cad(C1, ID1, Xs1, Ys1, Xd1, Yd1), Width=Xd1-Xs1, Lenght=Yd1-Ys1.
componentDimensionNet(ID1,Width,Lenght):- net(C1, ID1, Xs1, Ys1, Xd1, Yd1), Width=Xd1-Xs1, Lenght=Yd1-Ys1.


%calcolo la dimensione della box della Cad
boxCad(W,L):- #min{Xs1: cad(_,_,Xs1,_,_,_)} = K1, #max{Xs2: cad(_,_,_,_,Xs2,_)}= K2, W=K2-K1,
             #min{Ys1: cad(_,_,_,Ys1,_,_)} = K3, #max{Ys2: cad(_,_,_,_,_,Ys2)}= K4, L=K4-K3.

boxNet(W,L):- #min{Xs1: net(_,_,Xs1,_,_,_)} = K1, #max{Xs2: net(_,_,_,_,Xs2,_)}= K2, W=K2-K1,
             #min{Ys1: net(_,_,_,Ys1,_,_)} = K3, #max{Ys2: net(_,_,_,_,_,Ys2)}= K4, L=K4-K3.

intersectionThresholdCad(ID1,ID2,WT,LT):-componentDimensionCad(ID1,W1,L1),componentDimensionCad(ID2,W2,L2), intersectionPercentage(K),
                                        WT=W1*K/100,LT=L1*K/100.
intersectionThresholdNet(ID1,ID2,WT,LT):-componentDimensionNet(ID1,W1,L1),componentDimensionNet(ID2,W2,L2), intersectionPercentage(K),
                                        WT=W1*K/100,LT=L1*K/100.

distanceThresholdCad(DW,DL):- distancePercentage(A), boxCad(W,L), DW=W*A/100,DL=L*A/100.
distanceThresholdNet(DW,DL):- distancePercentage(A), boxNet(W,L), DW=W*A/100,DL=L*A/100.

%right cad
relCad(C1,ID1,C2,ID2,right,D):- cad(C1, ID1, Xs1, Ys1, Xd1, Yd1), cad(C2, ID2, KX, Ys2, Xd2, Yd2), inLevelCad(_,ID1,_,ID2,horizontal),
                        intersectionThresholdCad(ID1,ID2,WT,LT), #min{Xs3:cad(_,ID3,Xs3,_,_,_),inLevelCad(_,ID1,_,ID3,horizontal),Xs3>=Xd1-WT}=KX,D=KX-Xd1.

%top cad
relCad(C1,ID1,C2,ID2,top,D):-cad(C1, ID1, Xs1, Ys1, Xd1, Yd1), cad(C2, ID2, Xs2, Ys2, Xd2, KY), inLevelCad(_,ID1,_,ID2,vertical), 
                            intersectionThresholdCad(ID1,ID2,WT,LT), #max{Yd3:cad(_,ID3,_,_,_,Yd3),inLevelCad(_,ID1,_,ID3,vertical),Yd3<=Ys1+LT}=KY,D=Ys1-Ys2,
                            not auxRelCad(C1,ID1,C2,ID2,right),not auxRelCad(C2,ID2,C1,ID1,right).

%right net
relNet(C1,ID1,C2,ID2,right,D):- net(C1, ID1, Xs1, Ys1, Xd1, Yd1), net(C2, ID2, KX, Ys2, Xd2, Yd2), inLevelNet(_,ID1,_,ID2,horizontal),
                        intersectionThresholdNet(ID1,ID2,WT,LT), #min{Xs3:net(_,ID3,Xs3,_,_,_),inLevelNet(_,ID1,_,ID3,horizontal),Xs3>=Xd1-WT}=KX,D=KX-Xd1.

%top net
relNet(C1,ID1,C2,ID2,top,D):- net(C1, ID1, Xs1, Ys1, Xd1, Yd1), net(C2, ID2, Xs2, Ys2, Xd2, KY), inLevelNet(_,ID1,_,ID2,vertical), 
                            intersectionThresholdNet(ID1,ID2,WT,LT), #max{Yd3:net(_,ID3,_,_,_,Yd3),inLevelNet(_,ID1,_,ID3,vertical),Yd3<=Ys1+LT}=KY,D=Ys1-Ys2,
                            not auxRelNet(C1,ID1,C2,ID2,right),not auxRelNet(C2,ID2,C1,ID1,right).


auxRelNet(C1,ID1,C2,ID2,DIR):- relNet(C1,ID1,C2,ID2,DIR,D).
auxRelCad(C1,ID1,C2,ID2,DIR):- relCad(C1,ID1,C2,ID2,DIR,D).

%left
%relCad(C1,ID1,C2,ID2):-cad(C1, ID1, Xs1, Ys1, Xd1, Yd1), cad(C2, ID2, Xs2, Ys2, KX, Yd2), inLevelCad(_,ID1,_,ID2,horizontal),
%                        intersectionThresholdCad(ID1,ID2,WT,LT), #max{Xd3:cad(_,_,_,_,Xd3,_),Xd3<=Xs1+WT}=KX.

%down
%relCad(C1,ID1,C2,ID2):-cad(C1, ID1, Xs1, Ys1, Xd1, Yd1), cad(C2, ID2, Xs2, KY, Xd2, Yd2), inLevelCad(_,ID1,_,ID2,vertical),
%                        intersectionThresholdCad(ID1,ID2,WT,LT), #min{Ys3:cad(_,_,_,Ys3,_,_),Ys3>=Yd1+LT}=KY.


%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%heuristic to reduce false positive (error relations)

% considero una relazione se la distanza tra i due oggetti è minore di una certa soglia (percentuale della grandezza del box)
% considerando come origine il punto in alto a sinistra

limitedRelCad(C1,ID1,C2,ID2,D,"right"):- relCad(C1,ID1,C2,ID2,right,_),cad(C1, ID1, Xs1, Ys1, Xd1, Yd1), cad(C2, ID2, Xs2, Ys2, Xd2, Yd2), 
                                D=Xs2-Xd1,distanceThresholdCad(W,L), D<W.
                                

limitedRelCad(C1,ID1,C2,ID2,D,"top"):- relCad(C1,ID1,C2,ID2,top,_),cad(C1, ID1, Xs1, Ys1, Xd1, Yd1), cad(C2, ID2, Xs2, Ys2, Xd2, Yd2), 
                                D=Ys1-Ys2,distanceThresholdCad(W,L), D<L.
                                

limitedRelNet(C1,ID1,C2,ID2,D,"right"):- relNet(C1,ID1,C2,ID2,right,_),net(C1, ID1, Xs1, Ys1, Xd1, Yd1), net(C2, ID2, Xs2, Ys2, Xd2, Yd2), 
                                D=Xs2-Xd1,distanceThresholdNet(W,L), D<W.
                                

limitedRelNet(C1,ID1,C2,ID2,D,"top"):- relNet(C1,ID1,C2,ID2,top,_),net(C1, ID1, Xs1, Ys1, Xd1, Yd1), net(C2, ID2, Xs2, Ys2, Xd2, Yd2), 
                                D=Ys1-Ys2,distanceThresholdNet(W,L), D<L.                              
                                
                                
numRelations(net,N1,N2):- #count{ID1,ID2:relNet(C1,ID1,C2,ID2,DIR,_)}=N1,#count{ID1,ID2:limitedRelNet(C1,ID1,C2,ID2,DIS,_)}=N2.
numRelations(cad,N1,N2):- #count{ID1,ID2:relCad(C1,ID1,C2,ID2,DIR,_)}=N1,#count{ID1,ID2:limitedRelCad(C1,ID1,C2,ID2,DIS,_)}=N2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

%comparison between relations 

%Identifica le relazioni che sono presenti tra due componenti nella RETE ma non nel CAD
%noRelCad(X, Id1, Y, Id2) :- not #count{X,Y : posRelCad(X, _, Y, _, _)} >= 1, posRelNet(X, Id1, Y, Id2, _).

%Identifica le relazioni che sono presenti tra due componenti nel CAD ma non nella RETE
%noRelNet(X, Id1, Y, Id2) :- not #count{X,Y : posRelNet(X, _, Y, _, _)} >= 1, posRelCad(X, Id1, Y, Id2, _).


numRelationsCad(C1,C2,N):- #count{ID1,ID2:limitedRelCad(C1,ID1,C2,ID2,_,_)}=N, component(C1),component(C2).
numRelationsNet(C1,C2,N):- #count{ID1,ID2:limitedRelNet(C1,ID1,C2,ID2,_,_)}=N, component(C1),component(C2).

prob2(C1,C2):- numRelationsCad(C1,C2,N),numRelationsNet(C1,C2,N2), N!=N2.

absentRel(C1,C2,A):- numRelationsCad(C1,C2,N2), numRelationsNet(C1,C2,N1), A=N2-N1, A>0.
inExcessRel(C1,C2,A):-numRelationsCad(C1,C2,N2), numRelationsNet(C1,C2,N1), A = N1-N2, A>0.