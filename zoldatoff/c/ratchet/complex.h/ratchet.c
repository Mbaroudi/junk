#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <time.h>
#include <complex.h>

#define sqr(x) ((x)*(x))

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
double A[N_of_pixels], B, C;

// _________We generate jumps__________________
void Generate_Jumps ()
{
        int f, k = 0;
        double Sum = t;
        double rnd, q, T[100];
        T[0] = t;

        /*	for (k = 1; T[k] > 0.0; k++)
        	{
        		rnd = drand48();
        		if (rnd > 0.0)
        			T[k] = T[k-1] + log (rnd) / kappa;
        	}*/

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
        B = C  = 0.0;

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

                A_tmp -= sqr (q) * T[k] / 2 + M_PI_2 + q * T[k] * C;
                for (f = 0; f < N_of_pixels; f++)
                        A[f] += A_tmp - q * F[f] * sqr (T[k]) / 2;
                B += T[k] * q;
                C += q;
        }
}

//___________Calculating delta_p_________________________
void Calculate_delta_p ()
{
        register int f;
	int j;
        long k;
        double complex delta_p[N_of_pixels], R, Fi;
        double A1[N_of_pixels], A2[N_of_pixels];
        double B1, B2, C1, C2;
        FILE *output, *crash;

        output = fopen ("output.dat", "w");
        fclose(output);

        for (j = 1; j <= 2; j++) {
                t += 0.1;

                for (f = 0; f < N_of_pixels; f++)
                        delta_p[f] = 0.0;
                for (k = 1; k <= Very_Big_Number; k++) {
                        Generate_Jumps ();
                        for (f = 0; f < N_of_pixels; f++)
                                A1[f] = A[f];
                        B1 = B;
                        C1 = C;
                        Generate_Jumps ();
                        for (f = 0; f < N_of_pixels; f++)
                                A2[f] = A[f];
                        B2 = B;
                        C2 = C;

			Fi = - ( 4.0*sqr(B1-B2)*sqr(sigma) + 4.0*I*(B1-B2)*sigma*(C1+C2 - 2.0*p_0) + (C1-C2)*(C1-C2 + 8.0*I*x_0*sigma) ) / (8.0*sigma);
			R = - cexp(Fi) * ( C1+C2 - 2.0*p_0 + 2.0*I*(B1-B2)*sigma ) / 2.0;
			
                        for (f = 0; f < N_of_pixels; f++) 
				delta_p[f] = cexp(I*(A1-A2)) * R;
                        

                   /*     	crash = fopen ("crash", "w");
                        	fprintf (crash, "%f\n", k / Very_Big_Number);
                        	fclose (crash);
				printf("%f\%\n", 100 * k / Very_Big_Number);
		   */
                }

                for (f = 0; f < N_of_pixels; f++) {
                        delta_p[f] *= exp (2.0*kappa*t) / Very_Big_Number;
                        printf("F = %f\t", F[f]);
                        printf("delta_p_Re = %f\t", creal(delta_p[f]) );
                        printf("delta_p_Im = %f\n", cimag(delta_p[f]) );
                        output = fopen ("output.dat", "a");
                        fprintf(output, "%f\t", F[f]);
                        fprintf(output, "%f\t", creal(delta_p[f]) );
                        fprintf(output, "%f\n", cimag(delta_p[f]) );
                        fclose(output);
                }
        }

        output = fopen ("output.dat", "a");
        fprintf(output, "\nx_0 = %f\n", 1.0*x_0);
        fprintf(output, "p_0 = %f\n", 1.0*p_0);
        fprintf(output, "V_0 = %f\n", 1.0*V_0);
        fprintf(output, "sigma = %f\n", 1.0*sigma);
        fprintf(output, "t = %f\n", 1.0*t);
        fclose(output);
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

        printf("kappa = %f\n", kappa);
        Calculate_delta_p ();
        return 1;
}




