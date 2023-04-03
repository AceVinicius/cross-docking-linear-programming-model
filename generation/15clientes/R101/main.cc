//Instance generation (Paper 1)

#include <cstdlib>
#include <iostream>
#include <iomanip>
#include <fstream>
#include <sstream>
#include <cstring>
#include <ctime>
#include <cmath>

using namespace std;

// Function to transform a int in string funcao para trasnformar um int em string

string itos(int i)
{
    stringstream s;
    s << i;
    return s.str();
}

// Fuction to use qsort to order a vector

int compare( const void * a1 , const void * b1)
{
		if( *(double*)a1 > *(double*)b1)
		{
				return 1;
		}
		else
		{
			return -1;
		}
}

int main( int argc , char* argv[] )
{
        int i,j,p,f,l, h , t , ajust , od, tw , pt;
        int aux1, aux2, aux3, aux4,aux5,aux6 , aux7,aux8, aux9,aux10;
        int N;
        int K;
        int cap;
        int sementemestre;
        double* x;
        double* y;
        double* dem;
        double* a;
        double* b;
        double* st;
        double** dist;
        char nome[40];
        char prob[40];
        int semente[3][3][3];                      
               
        //quantidade mínimma de paletes para a geração das demandas
        int ini[]={2,4};
        //quantidade máxima de paletes para a geração das demandas
        int end[]={8,16};
        //quantidade de veículos de acordo com o intervalo
        int veiculos[] = {10 , 10};
        //número de posição na saida
        int nposicaoS[] = {9, 7};
        //quantidades de produtos
        int prod[]={10};
        //instantes iniciais dos intervalos
        int sup[]={5};        
        // número de docas de entrada;
        int indock[] = {3};
        // núnmero de docas de saída;
        int outdock[] = {3,4};
        // multiplicador
        int mult[] = {1,1,1}; 
        //volume de um palete
        double vol=1.2;
        //volume mínimo de um produto
        double vmin= 0.01*vol;
        //volume máximo de um produto
        double vmax= 0.1*vol;
        //tempo necessário para processar um palete
        double timepal = 5;
        //tempo necessário para o processamento da carga coletada
        double timeout = 30;
        // controla o tempo adicionado nas janelas de tempo
        //double ajuste[]= { 1.0 , 0.9};
        // percentual para apertar a janela
        double controle = 0.2;
        // Complexidade de manuseio
		double TH[]={0.5 , 0.6 , 0.7 ,0.8 , 0.9 , 1.0};
		
		// Complexidade de manuseio
		int ptype[]={20, 40, 100};
		
		double AJUST = 1;
		
		int MAXPROD = {3};
         
        
        //declarando os ponteiros        
        
        double* npal; //demanda de cada cliente em paletes 
        double** iprod;  //indica para cada cliente quais produtos são demandados 
        double** dprod; //quantidade de cada produto demandados por cada cliente
        double* vtotal; // volume total demandado por cada cliente
        double* vprod; // volume de cada produto
        double* cont; // contado para a quantidade de produtos que um cliente demanda
        double** volpp; // volume por produto demandado por cada cliente
        double* ptotal; // quantidade total de cada produto
        double* pcarga; // indica qual carga está cada produto
        double** rpcarga; // quantidades de cada produto que cada carga traz
        double* tcarga; // tempo de processamento de cada carga
        double* npalcarga; // número de palete de cada carga
        double* npalprod; // número de paletes necessário para trazer os produtos
        double* npalord;// número de paletes necessário para trazer os produtos ordenado
        int* nprodcarga; // número de produtos trazido por cada carga
        int* distr; // distribuicao dos produtos
        double* volcarga; // volume total trazido pela carga
        double* cargaord; // vetor com os tempos ordenados das cargas
        double* soma; // vetor para verificar as demandas dos produtos
        double* soma1; // vetor para verificar se existe algum produto se cliente
        double* sorteio; // vetor para o sorteio do produto
        double* sorteio1; // vertor para o sorteio do cliente
        double* voltotalp; // vetor para armazenar o volume total
        double** timew; // matriz com as janelas de tempo alteradas
        double* NUP; //number to update the times windows
        char* name; // string para o nome da instância
        char* instance;// nome da instância
        
        int* ntype; // número de tipos de produtos demandados por cada cliente
        
        double* soma2;
        double* soma3;
        double* npositionI;
        double* npositionO;
        double* intervaloTW;
        double* parteTW;
        
                     
           
        //abertura do arquivo

        argc--;
        argv++;

        if (argc < 1)
        {
            cerr << "Como usar o programa: ./ex dados.txt"<< endl;
            return 1;

        }

        ifstream arq(argv[0], ios::in);
        
                
        if (!arq)
        {
            cerr << "\n ** Erro: abrir abrir arquivo de entrada**\n"<< endl;
            exit(1); 
        }

        //leitura dos primeiros dados
        
        arq >> sementemestre;
        arq >> N;
        arq >> K;
        arq >> cap;

        // aloca a memória
       
        x= new double[N+2];
        y= new double[N+2];
        dem= new double[N+2];
        a= new double[N+2];
        b= new double[N+2];
        st= new double[N+2]; 
        dist = new double*[N+2];
        for (i=0; i<N+2;i++){
             dist[i]=new double[N+2];
        }

        //leitura dos dados restantes

		for (i=0; i<N+2;i++){
				arq >> x[i];
				arq >> y[i];
				arq >> dem[i];
				arq >> a[i];
				arq >> b[i];
				arq >> st[i];
	    }

	    arq >> nome;

	    for(i=0;i<10;i++){
	    	    prob[i]=nome[i];
	    }

        arq.close();
           
        srand(sementemestre);
        
        //gerando sementes

        for(t=0;t<2;t++){
			for(p=0;p<1;p++){
				for(f=0;f<1;f++){
					
					semente[t][p][f]= 100000+rand()%(1000000)+t*t+p*p+3*3;
				}
			}
			
		}
        
               

        //calculando as distâncias entre os clientes e os clintes e o depósito


        for(i=0; i < N+2;i++){
			for(j=0;j < N+2 ; j++){
				 dist[i][j] = sqrt((x[i]-x[j])*(x[i]-x[j])+(y[i]-y[j])*(y[i]-y[j]));
			}
		}
		
		
		for(tw=0;tw<6;tw++){
			for(pt=0;pt<3;pt++){
				for(t=0;t<2;t++){
					for(od=0;od<2;od++){
						for(p=0;p<1;p++){
							for(f=0;f<1;f++){
							//alocar a memória
					
							npal =  new double[N];
										
							iprod =  new double*[N];
							for(i=0;i<N;i++){
								iprod[i] = new double[prod[p]];
							}
					
							dprod =  new double*[N];
							for(i=0;i<N;i++){
								dprod[i] = new double[prod[p]];
							}
					
							vtotal = new double[N];
					
							intervaloTW = new double[N+1];
							parteTW = new double[N+1];
					
							vprod = new double[prod[p]];
							voltotalp = new double[prod[p]];
							cont = new double[N];
							soma = new double[N];
							soma1 = new double[prod[p]];
							sorteio = new double[N];
							sorteio1 = new double[prod[p]];
							soma2 = new double[1];
							NUP = new double[1];
							soma3 = new double[sup[f]];
							npositionO = new double[1];
					
							volpp =  new double*[N];
							for(i=0;i<N;i++){
								volpp[i] = new double[prod[p]];
							}
					
							pcarga = new double [prod[p]];
							ptotal = new double [prod[p]];
					
							rpcarga = new double*[prod[p]];
							for(j=0;j<prod[p];j++){
								rpcarga[j] = new double [sup[f]];
							}
					
							tcarga = new double [sup[f]];
							npalcarga = new double [sup[f]];
							npalprod = new double[prod[p]];
							npalord = new double[prod[p]];
							nprodcarga = new int [sup[f]];
							volcarga = new double [sup[f]];
							cargaord = new double [sup[f]];
							
							distr = new int [sup[f]];
					
							timew = new double*[N+2];
							for(i=0;i<N+2;i++){
								timew[i] = new double[2]; 
							}
							
							ntype = new int [N];
											
							name = new char [40];
							instance = new char [40];
					
							srand(semente[t][p][f]);
																
							// gerando a demanda em paletes e calculando o volume total
							for(i=0;i<N;i++){
								npal[i] = ini[t]+rand()%(end[t]-ini[t]+1);
								vtotal[i] = vol*npal[i];
							}
							// gerando o volume de cada produto
							for(j=0;j<prod[p];j++){
								vprod[j] = vmin + ((double) rand() / ((double) RAND_MAX +1))*(vmax-vmin);
							}
							
							//gerando o número de tipos de produtos demandados por cada cliente
							aux2 = (ptype[pt]*prod[p])/100;
							
							for(i=0;i<N;i++){
								ntype[i] = 1 + rand()%aux2;
							}
							
							// zerando a matriz iprod
							for(i=0;i<N;i++){
								for(j=0;j<prod[p];j++){
									iprod[i][j]=0;									
								}
							}
							
							//atribuindo os produtos aos clientes
							for(j=0;j<prod[p];j++){
								aux5 = 0;
								while(aux5 == 0){
									aux3 = rand()%N;
									if(ntype[aux3]>0){
										iprod[aux3][j]=1;
								        ntype[aux3] = ntype[aux3]-1;
								        aux5=1;
									}	
								}
							}
							
							// atribuindo os produtos restantes
							for(i=0;i<N;i++){
								while(*(ntype+i)>0){
									aux6 = 0;
									while(aux6==0){
										aux4 = rand()%prod[p];
										if(iprod[i][aux4]==0 && *(ntype+i)>0){
											iprod[i][aux4] = 1;
											ntype[i] = ntype[i] - 1;
											aux6 = 1;
										}	
									}																	
								}	
							}
															
							// contando a quantidade dos tipos de produtos diferentes que cada cliente demanda
							for(i=0;i<N;i++){
								cont[i]=0;
							}
					
							for(i=0;i<N;i++){
								for(j=0;j<prod[p];j++)
								{
									if(iprod[i][j]) cont[i]=cont[i]+1;
								}
							}
					
							// calculando o volume de cada produto demandandado pelos clientes
							// o volume será um número aleatório entre 40% e 60%  do dobro do volume médio por produto
							for(i=0;i<N;i++){
								for(j=0;j<prod[p];j++)
								{
									if(iprod[i][j])
									{
										volpp[i][j]= vtotal[i]/cont[i];
									}
								else
									{
										volpp[i][j]=0;
									}
								}
							}
					
							// calculando a demanda em unidade de cada produto para cada cliente
					
							for(i=0;i<N;i++){
								for(j=0;j<prod[p];j++)
								{
									if(iprod[i][j])
									{
										dprod[i][j]= floor(volpp[i][j]/vprod[j]);
									}
								else
									{
										dprod[i][j]=0;
									}
								}
							}	
					
							// calculando o total de cada produto
					
							for(j=0;j<prod[p];j++)
							{
								ptotal[j] = 0; 
							}
					
					
							for(j=0;j<prod[p];j++)
							{
								for(i=0;i<N;i++)
								{
									ptotal[j] = ptotal[j] + dprod[i][j]; 
								}
							}
					
							// calculando o volume total de cada produto
					
							for(j=0;j<prod[p];j++)
							{
								voltotalp[j] = ptotal[j]*vprod[j]; 
							}
							
							// calculando o número de paletes necessário para trazer cada tipo de produto
							
							for(j=0;j<prod[p];j++)
							{
								npalprod[j] = ceil(voltotalp[j]/vol); 
							}
							
													
							// designando os produtos para as cargas
							
							for(i=0;i<sup[f];i++){
								nprodcarga[i] = 1 + rand()%MAXPROD;
								distr[i]=0;
							}
							
							
							for(j=0;j<prod[p]+1;j++)
							{
								if(j<sup[f]){	
									aux10 = 0;
									while(aux10==0){
										aux9 = rand()%(sup[f]);
										if(distr[aux9]==0){
											nprodcarga[aux9] = nprodcarga[aux9] - 1;
											pcarga[j] = aux9;
											distr[aux9]=1;
											aux10 = 1;
										}	
									}	
								}
								else{
								aux7 = 0;
								while(aux7==0 && j<prod[p]){
									aux8 = rand()%(sup[f]);															
									if(nprodcarga[aux8]>=0){
										nprodcarga[aux8] = nprodcarga[aux8] - 1;
										pcarga[j] = aux8;
										aux7=1;									
									}
								}	
								}						
							}
									
																
							// calculando a matriz rpcargas com a informação da quantidade de cada produto que é trazida por cada carga
					
							for(j=0;j<prod[p];j++)
							{
								for(h=0;h<sup[f];h++)
								{
									if(pcarga[j]==h)
									{
										rpcarga[j][h]=ptotal[j];
									}
									else
									{
									rpcarga[j][h]=0;
									}
								}
							}
					
							
					
							// calculando o número de paletes de cada carga
					
							for(h=0;h<sup[f];h++)
							{
								npalcarga[h] = 0;
							}
					
							for(h=0;h<sup[f];h++)
							{
								for(j=0;j<prod[p];j++){
									if(rpcarga[j][h]){
										npalcarga[h]= npalcarga[h] + npalprod[j];
									}
								}
							}	
					
										
							// calculando o tempo de processamento de cada carga
					
							for(h=0;h<sup[f];h++)
							{
								tcarga[h]= npalcarga[h]*timepal;
							}
					
							//ordenando os tempos de processamento das carga na ordem crescente	
					
							for(h=0;h<sup[f];h++)
							{
								cargaord[h]= tcarga[h];
							}
					
							qsort(cargaord, sup[f], sizeof(double),compare);
					
							soma2[0] =0;
					
							for(h=0;h<sup[f];h++)
							{
								soma2[0]= soma2[0] + tcarga[h];
							}
					
					
					
					//atualizando as janelas do tempo dos clientes para a nossa instância
					//será somando ao limite inferior e superior soma da maior tempo de processamento entra as cargas recebidas com uma vez o tempo
					//de processamento da carga de saída
					NUP[0] = ceil(TH[tw]*(soma2[0]/indock[f]));
					
					timew[0][0] = a[0];
					timew[0][1] = b[0] + ceil(TH[tw]*(soma2[0]/indock[f]));
					
					
					timew[N+1][0] = a[N+1];
					timew[N+1][1] = timew[0][1];

					for(i=1;i<N+1;i++)
							{
								timew[i][0] = a[i] + ceil(TH[tw]*(soma2[0]/indock[f]));
								timew[i][1] = b[i] + ceil(TH[tw]*(soma2[0]/indock[f]));	
							}
							
							
							
					if(tw==0){
						strcpy(name,"05_");
					}
					
					if(tw==1){
						strcpy(name,"06_");
					}	
					
					if(tw==2){
						strcpy(name,"07_");
					}	
					
					if(tw==3){
						strcpy(name,"08_");
					}
					
					if(tw==4){
						strcpy(name,"09_");
					}	
					
					if(tw==5){
						strcpy(name,"10_");
					}		
							
						
							
						
					if(t==0){
						strcat(name,"C15_I1_");
					}
					else		
					{
						strcat(name,"C15_I2_");
					}
					
					if(od==0){
						strcat(name,"OD3_P10_S5_");
					}
					else{
						strcat(name,"OD4_P10_S5_");
						}
						
					
					if(pt==0){
						strcat(name,"20_");
					}
					else		
					{
						if(pt ==1){
							strcat(name,"40_");
						}
						else{
							strcat(name,"100_");
						}
					}
											
					strcat(name,nome);
					
					for(i=0;i<40;i++){
						instance[i] = name[i];
					}					
					ofstream saida(strcat(name,".txt"), ios::out);
					
        
					if (!saida)
						{
							cerr << "Arquivo de saida nao pode ser aberto!!" << endl;
					exit(1);
					}
					
					//imprimindo no arquivo
					
					saida << "Seed for function srand().#" << endl;
					saida << semente[t][p][f]<< endl ;
					saida << endl ;
					
					saida << "Inbound loads (suppliers).#"<< endl;
					saida << sup[f] << endl;
					saida << endl;
					
					saida << "Inbound docks.#" << endl;
					saida << indock[f]<< endl ;
					saida << endl ;
					
					saida << "Outbound docks.#" << endl;
					saida << outdock[od]<< endl ;
					saida << endl;
					
					saida << "Vehicle.#" << endl;
					saida << veiculos[t] << endl;
					saida << endl ;
					
					saida << "Vehicle capacity.#" << endl;
					saida << 16 << endl ;
					saida << endl ;
					
					saida << "Customers.#" << endl;
					saida << N << endl;
					saida << endl ;
					
					saida << "Number of products.#" << endl;
					saida << prod[p] << endl ;
					saida << endl ;
					
					saida << "Time to load one pallet .#" << endl;
					saida << 2 << endl ;
					saida << endl ;
					
					saida << "Service time per pallet.#" << endl;
					saida << 2 << endl ;
					saida << endl ;
					
					saida << "Changeover time.#" << endl;
					saida << 2 << endl ;
					saida << endl ;
					
					saida << "Processing time for inbound load.#" << endl;
					for(h=0;h< sup[f];h++)
					{
					saida << tcarga[h] << "  " ;
					}
					saida << endl;
					saida << endl ;
					
					saida << "Time window.#" << endl;
					for(i=0;i< N+2 ;i++)
					{
					saida << timew[i][0] << "  " << timew[i][1] << endl ;
					}
					saida << endl ;
					
					saida << "Quantity of required pallets per customer.#" << endl;
					for(i=0;i< N ;i++)
					{
					saida << npal[i] << "  " ;
					}
					saida << endl;
					saida << endl ;
										
					saida << "Quantity of required products per customer.#" << endl;
					for(j=0;j< prod[p] ;j++)
					{
						for(i=0;i<N;i++){
							saida << dprod[i][j] << "  " ;
						}
						saida << endl;
					}
					saida << endl;
					
					saida << "Number of each product into inbound loads.#" << endl;
					for(j=0;j< prod[p] ;j++)
					{
						for(h=0;h<sup[f];h++){
							saida << rpcarga[j][h] << "  " ;
						}
						saida << endl;
					}
					saida << endl;
					
					saida << "Volume of each product.#" << endl;
					for(j=0;j< prod[p] ;j++)
					{
					saida << setiosflags(ios::fixed | ios::showpoint | ios::left) << setprecision(2) << vprod[j] << "  " ;
					}
					saida << endl;
					saida << endl;			
					
					saida << "Distance (travel time).#" << endl;
					for(i=0;i<N+2;i++)
					{
						for(j=0;j<N+2;j++){
							saida << setiosflags(ios::fixed | ios::showpoint | ios::left) << setprecision(2) << dist[i][j] << "  " ;
						}
						saida << endl;
					}
					saida << endl;
					
					saida << "Number to update the time windows.#" << endl;
					saida << NUP[0]<< endl;	
					saida << endl;
					
					saida << "Instance.#" << endl;
					saida << instance << endl ;	
								
					saida.close();
					
					
					//libera memória
					delete[] npal;
					
					for (i = 0; i < N; i++){
						delete[] iprod[i];
					}
					delete[] iprod;
					
					for (i = 0; i < N; i++){
						delete[] dprod[i];
					}
					delete[] dprod;
					
					delete[] vtotal;

					delete[] intervaloTW;

					delete[] parteTW;

					delete[] vprod;
					
					delete[] voltotalp;

					delete[] cont;
					
					delete[] soma;
					
					delete[] soma1;

					delete[] sorteio;
					
					delete[] sorteio1;
					
					delete[] soma2;
					
					delete[] NUP;
					
					delete[] soma3;
					
					delete[] npositionO;

					for (i = 0; i < N; i++){
						delete[] volpp[i];
					}
					delete volpp;

					delete[] pcarga;

					delete[] ptotal;		
					
					for(j=0;j<prod[p];j++){
							delete rpcarga[j];
					}
					delete[] rpcarga;
					
					delete[] tcarga;
					
					delete[] npalcarga;
					
					delete[] npalprod;
					
					delete[] npalord;
					
					delete[] nprodcarga;
					
					delete[] volcarga;
					
					delete[] cargaord;
					
					for(i=0;i<N+2;i++){
							delete timew[i]; 
					}
					delete[] timew;
									
					delete[] name;
					
					delete[] distr;
					
					delete[] instance;
					
					delete[] ntype;
					
					
							
						}
					}
				}
			}
		}
	}	
	
    		
				
        delete[] x;
        delete[] y;
        delete[] a;
        delete[] b;
        delete[] st;
        delete[] dem;
        
        for (j = 0; j < N+2; j++)
        {
            delete[] dist[j];
		}
        delete[] dist;
        
       
        
        return 0;
         
}
