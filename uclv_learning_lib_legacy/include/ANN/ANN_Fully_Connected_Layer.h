
/*
    ANN_Fully_Connected_Layer

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

#ifndef ANN_FULLY_CONNECTED_LAYER_H
#define ANN_FULLY_CONNECTED_LAYER_H

#include <ANN/ANN_Layer_Interface.h>

#ifndef ANN_LAYER_ACTIVATION_FCN_DEFINITION
#define ANN_LAYER_ACTIVATION_FCN_DEFINITION 
#include "boost/function.hpp"
typedef boost::function< TooN::Vector<>(const TooN::Vector<>&) > ANN_LAYER_ACTIVATION_FCN;
#endif

class ANN_Fully_Connected_Layer : public ANN_Layer_Interface
{

private:

ANN_Fully_Connected_Layer(); //No default constructor

protected:

TooN::Matrix<> W_;
TooN::Vector<> b_;

ANN_LAYER_ACTIVATION_FCN activation_fcn_;

TooN::Vector<> output_;

public:

ANN_Fully_Connected_Layer( 
    const TooN::Matrix<>& W, 
    const TooN::Vector<>& b, 
    const ANN_LAYER_ACTIVATION_FCN& activation_fcn 
    )
    : W_(W),
      b_(b),
      activation_fcn_(activation_fcn),
      output_( TooN::Zeros( W.num_rows() ))
      {
          if(!check_sizes())
          {
              std::cout << "ERROR IN SIZE OF ANN_Fully_Connected_Layer" << std::endl;
              exit(-1);
          }
      }

ANN_Fully_Connected_Layer( const ANN_Fully_Connected_Layer& l) = default;

virtual ANN_Fully_Connected_Layer* clone() const override
{
    return new ANN_Fully_Connected_Layer(*this);
}

virtual ~ANN_Fully_Connected_Layer() override = default;

/*=============RUNNER===========================*/
inline virtual const TooN::Vector<>& compute( const TooN::Vector<>& input ) override
{
    output_ = activation_fcn_((W_*input) + b_);
    return output_;
}

/*
inline virtual TooN::Vector<> compute( const TooN::Vector<>& input ) const override
{
    return activation_fcn_((W_*input) + b_);
}
*/

/*==============================================*/

virtual bool check_sizes() const
{
    if(W_.num_rows() != b_.size()){
        return false;
    }
    if(output_.size() != b_.size()){
        return false;
    }
    return true;
}

};

using ANN_Fully_Connected_Layer_Ptr = std::unique_ptr<ANN_Fully_Connected_Layer>;

#endif