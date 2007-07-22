#include <stdlib.h>
#include <stdio.h>
#include <math.h>
#include <time.h>

/*******�������������� ��� ������������� ������������ ���������� ��������� �����************/
#ifndef SFMT
#define SFMT
#include "sfmt19937-sse2.c"
#endif
/*******�������������� ��� ������������� ������������ ���������� ��������� �����************/

#ifndef M_PI
#define M_PI 3.141592654
#endif

/*********��������� �������*********/
#define result_file "matrix.dat"
#define NN 4
const int Ntraj = 1e6;
const double V0 = 1.0;
const double E0 = 0.0;
const double Tmax = 0.1;
const int Nmax = 128;
const int DiamP = 8;
/*********��������� �������*********/

double kappa;
double m2;
double A[NN+1];
double P[NN+1];

struct str {
        double tau;
        double t;
        double d;
        double p;
} p_str[10];

struct compl {
        double re;
        double im;
} Mat[513][513];

double RAND() {
#ifdef SFMT
	return genrand_real1();
#else
	return rand()/(double)RAND_MAX;
#endif	
}

inline double V (double x, int M, float V0) {
        int i;
        double result = 0.;
        for (i=1; i<=M; i++) result += sin(i*x)/i;
        return V0 * result;
}

inline double Phi(double x) {
        if (x<0.) return M_PI/2.;
        else return M_PI*3./2.;
}

inline double R(double t) {
        return 4.*sqrt(m2*kappa*t);
}

inline int randd(void) {
        double r = 25./12.* RAND();
        int k;
        if (r<=A[1]) k = 1;
        else if (r<=A[2]) k = 2;
             else if (r<=A[3]) k = 3;
                       else k = 4;

        if (RAND() <= .5) k = -k;
        return k;
}

inline void trajectory(double* act) {
        /*trajectory tau, t, d, p*/
        int k, j = 1;
        p_str[1].t = p_str[1].p = 0.;
        while ( p_str[j].t <= Tmax ) {
                p_str[j].tau = log( 1/(RAND() + 0.0000001 ) ) / kappa;
                p_str[j].d = randd();
                j++;
                p_str[j].t = p_str[j-1].t + p_str[j-1].tau;
                p_str[j].p = p_str[j-1].p + p_str[j-1].d;
        }


        if (j>1) p_str[j-1].tau = Tmax - p_str[j-1].t;
        else p_str[j].t = Tmax;
        /*end trajectory*/
        j--;

        if (j == 1) act[1] = act[2] = act[3] = act[4] = 0.;
        else {
                act[1] = j-1;
                act[2] = p_str[j].p;
                act[3] = act[4] = 0.;
                for (k=1; k<=j-1;k++)  {
                        act[3] += p_str[k].tau * (p_str[k].p + E0*(p_str[k+1].t-p_str[k].tau/2.));
                        act[4] += Phi(p_str[k].d) +
                                  ( M_PI + p_str[k].tau*( p_str[k].p + E0*( p_str[k].t-p_str[k].tau/2. )*( p_str[k].t-p_str[k].tau/2. )
                                                          + E0*E0 * p_str[k].tau * p_str[k].tau * p_str[k].tau / 12. )
                                  ) / 2.;
                }
        }
}

inline int Round(double x) {
        if (ceil(x)-x <= x-floor(x)) return (int) ceil(x);
        else return (int) floor(x);
}

int main() {
        register int i, j, k;
        int ntr = 0, cnt = 0, p0 = 0;
        int E0Shift, Corr, MS, MSS;
        double RC, h, EKT, pk;
        double s, p, q;
        double ACT[5];
        FILE* fresult;
	time_t time_begin;
	double time_left;

#ifdef SFMT
	init_gen_rand(time(NULL));
#else	
        srand(time(NULL));
#endif	

        for (i=1; i<=NN; i++) {
                A[i] = 0.;
                for (k=1; k<=i; k++) A[i] += 1./k;
        }

        for (k=1; k<=NN; k++) P[k] = .5/k/A[NN];

        printf("�������� �����: %.2f\n", Tmax);
        printf("���������� ����������: %.1e\n", (double) Ntraj);

        kappa = V0 * A[NN];
        printf("Kappa: %.4f\n", kappa);

        m2 = 0.;
        for (k=1; k<=NN; k++) m2 += 2*P[k]*k*k;
        printf("m2: %.4f\n", m2);

        RC = R(Tmax);
        printf("������ ��������: %.2f\n", RC);

        h = (RC + DiamP) / Nmax;
        printf("��� �����: %.2f\n", h);

        E0Shift = floor(E0*Tmax/h);
        printf("���������� ����� ����� � ������ �� E0: %i\n", E0Shift);

        Corr = floor(RC/h);
        printf("����� ����� ����� � ��������: %i\n", Corr);

        MS = Corr + floor(DiamP/h) + floor(abs(E0)*Tmax/h);
        MSS = 2*MS + 1;
        printf("����������� �������, ���������������� ����������� ��������: %i\n", MSS);

        EKT = exp(kappa*Tmax)/Ntraj;

        for (i=1;i<=MSS;i++)
        for (j=1;j<=MSS;j++)
                if (i!=j) Mat[i][j].re = Mat[i][j].im = 0.;
                else {
                        Mat[i][j].re = 1./Ntraj/Ntraj;
                        Mat[i][j].im = 0.;
                }

	time_begin = time(NULL);
	
	printf("\n������� ����������:\n");
	
        while (ntr < Ntraj) {
                ntr++;
		if ( ntr% (Ntraj/10) == 0 ) {
			printf(" %d%%", 100*ntr/Ntraj);
			time_left = (time(NULL) - time_begin) / 60. / ntr * (Ntraj-ntr);
			if (time_left >= 1.) printf(" [�������� %.2f �����]\n", time_left);
			else printf(" [�������� %.0f ������]\n", time_left*60.);
			fflush(stdout);
		}
		else if ( ntr% (Ntraj/10/10) == 0 ) {
			printf("=");
			fflush(stdout);
			}

                trajectory(ACT);

                if (ACT[1] > 0.) {
                        p = ACT[2];
                        q = ACT[3];
                        //double delta = p/h - j1;
                        s = ACT[4];
                        if (abs(p)>RC)	cnt++;
                        else for (k=1; k<=MSS;k++) {
                                pk = p0 + (k-MS)*h;
                                i = (Round(p/h) - E0Shift + k) % MSS;
                                Mat[k][i].re += //(1 - delta)
                                          cos(s-q*pk+pk*pk*Tmax/2.) * EKT;
                                Mat[k][i].im += //(1 - delta)
                                          sin(s-q*pk+pk*pk*Tmax/2.) * EKT;

                                //Mat[k+1][i].re += delta * cos(s-q*pk+pk*pk*Tmax/2.) * EKT;
                                //Mat[k+1][i].im += delta * sin(s-q*pk+pk*pk*Tmax/2.) * EKT;
                        }
                }
                else for (k=1;k<=MSS;k++) {
                        pk = p0 + (k-MS)*h;
                        i = (k-E0Shift) % MSS;
                        Mat[k][i].re += cos( (pk*pk-pk*E0*Tmax+ (E0*Tmax*E0*Tmax) /3. )*Tmax/2. ) * EKT;
                        Mat[k][i].im += sin( (pk*pk-pk*E0*Tmax+ (E0*Tmax*E0*Tmax) /3. )*Tmax/2. ) * EKT;
                }
        }

        printf("\n����������� �������� �������: %.2f%%\n", (double) cnt/ (double) Ntraj * 100.);

        fresult = fopen(result_file,"w");
        fprintf(fresult, "{");
        for (i=1;i<=MSS;i++) {
                fprintf(fresult, "{");
                for (j=1;j<=MSS;j++) {
                        if (fabs(Mat[i][j].im) + fabs(Mat[i][j].re) > 1e-10)
                                if (Mat[i][j].im < 0)
                                        fprintf(fresult, "%.10f - %.10f*I", Mat[i][j].re, -Mat[i][j].im);
                                else
                                        fprintf(fresult, "%.10f + %.10f*I", Mat[i][j].re, Mat[i][j].im);
                        else fprintf(fresult, "0");
                        if (j<MSS) {
                                fprintf(fresult, ", ");
                        }
                }
                if (i<MSS) fprintf(fresult, "}, ");
                else fprintf(fresult, "}");
        }
        fprintf(fresult, "}");
        fclose(fresult);

        return 0;
}

