/*
    ANN MAP MIN MAX LAYER

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

#ifndef ANN_MAPMINMAX_LAYER_H
#define ANN_MAPMINMAX_LAYER_H

#include <ANN/ANN_Layer_Interface.h>

class ANN_MapMinMax : public ANN_Layer_Interface
{

private:

ANN_MapMinMax(); //No default constructor

protected:

TooN::Vector<> max_;
TooN::Vector<> min_;
TooN::Vector<> output_;
bool b_apply;

public:

ANN_MapMinMax( 
    const TooN::Vector<>& min, 
    const TooN::Vector<>& max,
    bool b_reverse = false
)
:min_(min),
max_(max),
output_(TooN::Zeros(min.size())),
b_apply(!b_reverse)
{
    if(!check_sizes())
    {
        std::cout << "ERROR IN SIZE OF ANN_MapMinMax" << std::endl;
        exit(-1);
    }
}

ANN_MapMinMax( const ANN_MapMinMax& l) = default;

virtual ANN_MapMinMax* clone() const override
{
    return new ANN_MapMinMax(*this);
}

virtual ~ANN_MapMinMax() override = default;

/*=============RUNNER===========================*/

inline virtual const TooN::Vector<>& compute( const TooN::Vector<>& input ) override
{
    if( b_apply ){
        return apply( input );
    } else {
        return reverse( input );
    }
}

/*
inline virtual TooN::Vector<> compute( const TooN::Vector<>& input ) const override
{
    if( b_apply ){
        return apply( input );
    } else {
        return reverse( input );
    }
}
*/

/*==============================================*/

/*=============METHODS===========================*/

inline virtual const TooN::Vector<>& apply( const TooN::Vector<>& input )
{
    for (int s = 0; s < max_.size(); s++)
    {
		output_[s] = ((2.0 / (max_[s] - min_[s])) * (input[s] - min_[s])) - 1.0; 
	}
	return output_;
}

/*
inline virtual TooN::Vector<> apply( const TooN::Vector<>& input ) const
{
    TooN::Vector<> output(TooN::Zeros(max_.size()));
    for (int s = 0; s < max_.size(); s++)
    {
		output[s] = ((2.0 / (max_[s] - min_[s])) * (input[s] - min_[s])) - 1.0; 
	}
	return output;
}
*/

inline virtual const TooN::Vector<>& reverse( const TooN::Vector<>& input )
{
    for (int h = 0; h < max_.size(); h++)
    {  
	    output_[h] = ( (max_[h] - min_[h]) / 2.0 * (input[h] + 1.0) + min_[h] );
	}
	return output_;
}

/*
inline virtual TooN::Vector<> reverse( const TooN::Vector<>& input ) const
{
    TooN::Vector<> output(TooN::Zeros(max_.size()));
    for (int h = 0; h < max_.size(); h++)
    {  
	    output[h] = ( (max_[h] - min_[h]) / 2.0 * (input[h] + 1.0) + min_[h] );
	}
	return output;
}
*/

virtual bool check_sizes() const
{
    if(max_.size() != min_.size()){
        return false;
    }
    if(output_.size() != min_.size()){
        return false;
    }
    return true;
}

/*==============================================*/

};

using ANN_MapMinMax_Ptr = std::unique_ptr<ANN_MapMinMax>;

#endif