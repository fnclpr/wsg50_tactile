/*
    ANN Class

    Copyright 2017-2019 Università della Campania Luigi Vanvitelli

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

#ifndef ANN_H
#define ANN_H

#include <ANN/ANN_Layer_Interface.h>

class ANN : public ANN_Layer_Interface
{

private:

protected:

std::vector<ANN_Layer_Interface_Ptr> layers_;

public:

ANN() = default;

ANN( const ANN& ann)
{
    for( const auto &layer : ann.layers_ )
    {
        layers_.push_back( ANN_Layer_Interface_Ptr( layer->clone() )  );
    }
}

virtual ANN* clone() const override
{
    return new ANN(*this);
}

virtual ~ANN() override = default;

void push_back_Layer( const ANN_Layer_Interface& layer )
{
    layers_.push_back( ANN_Layer_Interface_Ptr( layer.clone() ) );
}

/*=============RUNNER===========================*/
inline virtual const TooN::Vector<>& compute( const TooN::Vector<>& input ) override
{

    const TooN::Vector<>* output = &input;
    for( auto &layer : layers_ )
    {
        output = &layer->compute(*output);
    }
    return *output;

}

/*==============================================*/

};

#endif