/*
    Helper Functions to read ANN from file

    Copyright 2019 Università della Campania Luigi Vanvitelli

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
*/

#include <ANN/ANN_File_Reader.h>

#ifndef SUN_COLORS
#define SUN_COLORS

/* ======= COLORS ========= */
#define CRESET   "\033[0m"
#define BLACK   "\033[30m"      /* Black */
#define RED     "\033[31m"      /* Red */
#define GREEN   "\033[32m"      /* Green */
#define YELLOW  "\033[33m"      /* Yellow */
#define BLUE    "\033[34m"      /* Blue */
#define MAGENTA "\033[35m"      /* Magenta */
#define CYAN    "\033[36m"      /* Cyan */
#define WHITE   "\033[37m"      /* White */
#define BOLD    "\033[1m"       /* Bold */
#define BOLDBLACK   "\033[1m\033[30m"      /* Bold Black */
#define BOLDRED     "\033[1m\033[31m"      /* Bold Red */
#define BOLDGREEN   "\033[1m\033[32m"      /* Bold Green */
#define BOLDYELLOW  "\033[1m\033[33m"      /* Bold Yellow */
#define BOLDBLUE    "\033[1m\033[34m"      /* Bold Blue */
#define BOLDMAGENTA "\033[1m\033[35m"      /* Bold Magenta */
#define BOLDCYAN    "\033[1m\033[36m"      /* Bold Cyan */
#define BOLDWHITE   "\033[1m\033[37m"      /* Bold White */
/*===============================*/

#endif

#define NO_LAYER_CODE                   0
#define PCA_LAYER_CODE                  1
#define MAPMINMAX_LAYER_CODE            2
#define MAPMINMAX_REVERSE_LAYER_CODE    3
#define FULLY_CONNECTED_LAYER_CODE      4

#define SIGMOID_FUNCTION_CODE   1
#define LINEAR_FUNCTION_CODE    2

inline int readIntegerFile(FILE *f);
inline TooN::Matrix<> readFileM(FILE *f, unsigned int n_r, unsigned int n_c);
inline TooN::Vector<> readFileV(FILE *f, unsigned int dim);

ANN readANNFile( const std::string file_path )
{

    //Open File
    FILE *f;
	f = fopen(file_path.c_str(), "r");

    //Chek exist...
	if (f == NULL){
		printf(BOLDRED "Error opening file..." CRESET);
		printf(BOLDBLUE " %s\n" CRESET,file_path.c_str());
        printf(BOLDBLUE " Does the file exist?\n" CRESET);
		throw std::runtime_error("Could not open file");
	}

    int layer_type = readIntegerFile(f);

    ANN ann;

    while( layer_type != NO_LAYER_CODE )
    {
        switch (layer_type)
        {
            case PCA_LAYER_CODE:
            {
                ann.push_back_Layer( readPCALayerFile(f) );
                break;
            }
            case MAPMINMAX_LAYER_CODE:
            {
                ann.push_back_Layer( readMapMinMaxLayerFile(f) );
                break;
            }
            case MAPMINMAX_REVERSE_LAYER_CODE:
            {
                ann.push_back_Layer( readMapMinMaxLayerFile(f, true) );
                break;
            }
            case FULLY_CONNECTED_LAYER_CODE:
            {
                ann.push_back_Layer( readFullyConnectedLayerFile(f) );
                break;
            }
            default:
            {
                printf(BOLDRED "Error Non Valid Layer type %d" CRESET, layer_type);
                fclose(f);
                throw std::runtime_error("Non Valid Layer type");
            }
        }

        layer_type = readIntegerFile(f);

    }

    fclose(f);

    return ann;

}

inline int readIntegerFile(FILE *f)
{
    double out_dbl;
    fscanf(f, "%lf,", &out_dbl);
    return (int)out_dbl;
}

inline TooN::Matrix<> readFileM(FILE *f, unsigned int n_r, unsigned int n_c)
{
	TooN::Matrix<> out = TooN::Zeros(n_r,n_c);
	double tmp;
	for (int i = 0; i < n_r; i++) {
		for (int j = 0; j < n_c; j++) {
			fscanf(f, "%lf", &tmp);
			out[i][j] = tmp;
		}
	}
	return out;
}

inline TooN::Vector<> readFileV(FILE *f, unsigned int dim)
{
	TooN::Vector<> out = TooN::Zeros(dim);
	double tmp;
	for (int i = 0; i < dim; i++) {
		fscanf(f, "%lf,", &tmp);
		out[i] = tmp;
	}
	return out;
}

ANN_PCA_Layer readPCALayerFile(FILE *f)
{
    int sizeInput = readIntegerFile(f);
    int sizeOutput = readIntegerFile(f);

    TooN::Vector<> pca_mean = readFileV(f, sizeInput);
    TooN::Matrix<> Ureduce = readFileM(f, sizeInput, sizeOutput);

    return ANN_PCA_Layer( 
        pca_mean,
        Ureduce
    );
}

ANN_MapMinMax readMapMinMaxLayerFile(FILE *f, bool b_reverse)
{
    int numElements = readIntegerFile(f);

    TooN::Vector<> min = readFileV(f, numElements);
    TooN::Vector<> max = readFileV(f, numElements);

    return ANN_MapMinMax( 
        min, 
        max,
        b_reverse
    );
}

ANN_Fully_Connected_Layer readFullyConnectedLayerFile(FILE *f)
{
    int sizeInput = readIntegerFile(f);
    int numNeurons = readIntegerFile(f);
    int activation_fcn_type = readIntegerFile(f);

    TooN::Matrix<> W = readFileM(f, numNeurons, sizeInput);
    TooN::Vector<> b = readFileV(f, numNeurons);

    switch (activation_fcn_type)
    {
        case SIGMOID_FUNCTION_CODE:
        {
            return ANN_Fully_Connected_Layer( 
                W, 
                b, 
                ANN_SIGMA_ACTIVATION_FCN
            );
        }
        case LINEAR_FUNCTION_CODE:
        {
            return ANN_Fully_Connected_Layer( 
                W, 
                b, 
                ANN_LINEAR_ACTIVATION_FCN
            );
        }
        default:
        {
            printf(BOLDRED "Error Non Valid activation_fcn_type %d" CRESET, activation_fcn_type);
            fclose(f);
            throw std::runtime_error("Non Valid activation_fcn_type");
        }
    }
}
