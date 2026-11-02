
/*
    ANN_Layer_Interface

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

#ifndef ANN_LAYER_INTERFACE_H
#define ANN_LAYER_INTERFACE_H

#include <TooN/TooN.h>
#include <memory>

class ANN_Layer_Interface
{

private:

protected:

public:

ANN_Layer_Interface() = default;

ANN_Layer_Interface( const ANN_Layer_Interface& l) = default;

virtual ANN_Layer_Interface* clone() const = 0;

virtual ~ANN_Layer_Interface() = default;

/*=============RUNNER===========================*/
virtual const TooN::Vector<>& compute( const TooN::Vector<>& input ) = 0;
//virtual TooN::Vector<> compute( const TooN::Vector<>& input ) const = 0;
/*==============================================*/

};

using ANN_Layer_Interface_Ptr = std::unique_ptr<ANN_Layer_Interface>;

#endif