#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>

#define sqr(x) ((x)*(x))
#define sincos(x,s,c) sincos_x87_inline(x,s,c)
inline void sincos_x87_inline(double x,double *s,double *c)
{
__asm__ ("fsincos;" : "=t" (*c), "=u" (*s) : "0" (x) : "st(7)");
}

#define p_0 0.0
#define x_0 1.0
#define sigma 1.0
#define V_0 1.0
#define Very_Big_Number 5.0e5
#define N_of_pixels 100
#define Max_F 2000.0

double F[N_of_pixels];
double t = 0.10;
double kappa = 0.0;

// _________We generate jumps__________________
void Generate_Jumps (double A[], double* B, double* C)
{
        int f, k = 0;
        double Sum = t;
        double rnd, q, T[100];
        T[0] = t;

        while (Sum > 0.0) {
                rnd = drand48();
                if (rnd > 0.0)
                        Sum += log (rnd) / kappa;
                T[++k] = Sum;
        }

        int N_of_jumps = k;
        T[N_of_jumps] = 0.0;

        for (f = 0; f < N_of_pixels; f++)
                A[f] = 0.0;
        double A_tmp = 0.0;
        *B = *C  = 0.0;

        for (k = 1; k <= N_of_jumps; k++) {
                rnd = kappa * drand48() / V_0;
                int j = 0;
                Sum = 0.0;

                while (rnd > Sum)
                        Sum += 1.0 / (++j);

                if (drand48() < 0.5) {
                        q = -j;
                        A_tmp = M_PI_2;
                } else {
                        q = j;
                        A_tmp = - M_PI_2;
                }

                A_tmp -= sqr (q) * T[k] / 2 + M_PI_2 + q * T[k] * *C;
                for (f = 0; f < N_of_pixels; f++)
                        A[f] += A_tmp - q * F[f] * sqr (T[k]) / 2;
                *B += T[k] * q;
                *C += q;
        }
}

//___________Calculating delta_p_________________________
void Calculate_delta_p ()
{
        register int f;
        int j;
        long k;
        double delta_p_Re[N_of_pixels], delta_p_Im[N_of_pixels];
        double A1[N_of_pixels], A2[N_of_pixels];
        double B1, B2, C1, C2;
        double tmp_sin, tmp_cos;
        double tmp_exp, tmp1, tmp2;
        double Fi_Im, Fi_Re;
        double R_Im, R_Re;
        FILE *output, *crash;

        output = fopen ("output.dat", "w");
        fclose(output);

        for (j = 1; j <= 2; j++) {
                t += 0.1;

                for (f = 0; f < N_of_pixels; f++)
                        delta_p_Re[f] = delta_p_Im[f] = 0.0;
                for (k = 1; k <= Very_Big_Number; k++) {
                        Generate_Jumps (A1, &B1, &C1);
                        Generate_Jumps (A2, &B2, &C2);
                        
                        tmp1 = 2.0 * (B1-B2) * sigma;
                        tmp2 = C1 + C2 - 2.0*p_0;
                        Fi_Re = - (sqr (tmp1) + sqr (C1 - C2)) / (8.0*sigma);
                        Fi_Im =  - (2.0 * tmp1 * tmp2 + 8.0 * x_0 * sigma * (C1 - C2)) / (8.0*sigma);
                        //__builtin_sincos(Fi_Im, &tmp_sin, &tmp_cos);
                        sincos(Fi_Im, &tmp_sin, &tmp_cos);
                        tmp_exp = exp (Fi_Re);
                        R_Re = - tmp_exp * (tmp_cos * tmp2 - tmp_sin * tmp1) / 2.0;
                        R_Im = - tmp_exp * (tmp_sin * tmp2 + tmp_cos * tmp1) / 2.0;

                        for (f = 0; f < N_of_pixels-1; f++) {
                                //__builtin_sincos(A1[f]-A2[f], &tmp_sin, &tmp_cos);
                                sincos(A1[f]-A2[f], &tmp_sin, &tmp_cos);
                                __builtin_prefetch(&A1[f+1], 1, 3);
                                __builtin_prefetch(&A2[f+1], 1, 3);
                                delta_p_Re[f] += tmp_cos * R_Re - tmp_sin * R_Im;
                                //delta_p_Im[f] += tmp_sin * R_Re + tmp_cos * R_Im;
                        }

                        /*     	
			crash = fopen ("crash", "w");
                        fprintf (crash, "%f\n", k / Very_Big_Number);
                        fclose (crash);
                        printf("%f\%\n", 100 * k / Very_Big_Number);
                        */
                }

                output = fopen ("output.dat", "a");
		tmp_exp = exp (2.0*kappa*t) / Very_Big_Number;
                for (f = 0; f < N_of_pixels; f++) {
                        delta_p_Re[f] *= tmp_exp;
                        //delta_p_Im[f] *= tmp_exp;
                        printf("F = %f\t", F[f]);
                        printf("delta_p_Re = %f\n", delta_p_Re[f]);
                        //printf("delta_p_Im = %f\n", delta_p_Im[f]);
                        fprintf(output, "%f\t", F[f]);
                        fprintf(output, "%f\n", delta_p_Re[f]);
                        //fprintf(output, "%f\n", delta_p_Im[f]);
                }
                fprintf(output, "\n# x_0 = %f\n", 1.0*x_0);
                fprintf(output, "# p_0 = %f\n", 1.0*p_0);
                fprintf(output, "# V_0 = %f\n", 1.0*V_0);
                fprintf(output, "# sigma = %f\n", 1.0*sigma);
                fprintf(output, "# t = %f\n", 1.0*t);
                fclose(output);
        }
}

int main ()
{
        int k, f;

        srand48 ((long) time(NULL));

        for (k = 1; k <= 8; k++) {
                kappa += V_0/k;
        }

        for (f = 0; f < N_of_pixels; f++) {
                F[f] = -Max_F + f * 2.0 * Max_F / N_of_pixels;
        }

        Calculate_delta_p ();
        return 1;
}




