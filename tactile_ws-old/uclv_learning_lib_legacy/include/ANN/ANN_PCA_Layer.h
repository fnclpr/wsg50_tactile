/*
    ANN MAP PCA LAYER

    Copyright 2019 Università della Campania Luigi Vanvitelli

	Author: Marco Costanzo <marco.costanzo@unicampania.it>

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

#ifndef ANN_PCA_LAYER_H
#define ANN_PCA_LAYER_H

#include <ANN/ANN_Layer_Interface.h>

class ANN_PCA_Layer : public ANN_Layer_Interface
{

private:

ANN_PCA_Layer(); //No default constructor

protected:

TooN::Vector<> pca_mean_;
TooN::Matrix<> Ureduce_T_;
TooN::Vector<> output_;

public:

ANN_PCA_Layer( 
    const TooN::Vector<>& pca_mean,
    const TooN::Matrix<>& Ureduce
)
:pca_mean_(pca_mean),
Ureduce_T_(Ureduce.T()),
output_(Ureduce_T_.num_rows())
{
    if(!check_sizes())
    {
        std::cout << "ERROR IN SIZE OF ANN_PCA_Layer" << std::endl;
        exit(-1);
    }
}

ANN_PCA_Layer( const ANN_PCA_Layer& l) = default;

virtual ANN_PCA_Layer* clone() const override
{
    return new ANN_PCA_Layer(*this);
}

virtual ~ANN_PCA_Layer() override = default;

/*=============RUNNER===========================*/

inline virtual const TooN::Vector<>& compute( const TooN::Vector<>& input ) override
{
    output_ = Ureduce_T_ * ( input - pca_mean_ );
    return output_;
}

/*
inline virtual TooN::Vector<> compute( const TooN::Vector<>& input ) const
{
    return Ureduce_T_ * ( input - pca_mean_ );
}
*/

/*==============================================*/

virtual bool check_sizes() const
{
    if(Ureduce_T_.num_cols() != pca_mean_.size()){
        return false;
    }
    if(Ureduce_T_.num_rows() != output_.size()){
        return false;
    }
    return true;
}

/*==============================================*/

};

using ANN_PCA_Layer_Ptr = std::unique_ptr<ANN_PCA_Layer>;

#endif