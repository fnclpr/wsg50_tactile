
/*
    ANN Layer activation functions

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

#ifndef ANN_ACTIVATION_FCNS_H
#define ANN_ACTIVATION_FCNS_H

#include <TooN/TooN.h>

#ifndef ANN_LAYER_ACTIVATION_FCN_DEFINITION
#define ANN_LAYER_ACTIVATION_FCN_DEFINITION 
#include "boost/function.hpp"
typedef boost::function< TooN::Vector<>(const TooN::Vector<>&) > ANN_LAYER_ACTIVATION_FCN;
#endif

inline TooN::Vector<> ANN_SIGMA_ACTIVATION_FCN(const TooN::Vector<>& x)
{
    TooN::Vector<> out = TooN::Zeros(x.size());
    for(int i = 0; i < x.size(); i++ )
		out[i] = (2.0 / (1.0 + exp(-2.0 * x[i])) - 1.0);
	return out;
}

inline TooN::Vector<> ANN_LINEAR_ACTIVATION_FCN(const TooN::Vector<>& x)
{ 
    return x; 
}

#endif