/*

    Algorithms for machine learning

    Copyright 2018 Università della Campania Luigi Vanvitelli

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

#include "learn_algs/learn_algs.h"


double findZero(double initial_point, const boost::function<double(double)>& Jcst, const boost::function<double(double)>& gradJ, double GD_GAIN, double GD_COST_TOL, double lambda, int MAX_GD_ITER, bool& b_max_iter ){

    double JJ = Jcst(initial_point);
	bool converge = false;
	int num_iter = 0;

    double x = initial_point;

	while( !converge && (num_iter<MAX_GD_ITER) && !std::isnan(x) ){

		//x = x - GD_GAIN * JJ * (1.0 / gradJ(x) );
        double grad = gradJ(x);
		x = x - GD_GAIN * JJ * (grad / ( grad*grad + lambda ) );
		JJ = Jcst(x);
		converge = (fabs(JJ) < GD_COST_TOL);				
		num_iter++;

	}

    if(num_iter >= MAX_GD_ITER)
        b_max_iter = true;
    else
        b_max_iter = false;

    return x;
}

double findZero(double initial_point, const boost::function<double(double)>& Jcst, const boost::function<double(double)>& gradJ, double GD_GAIN, double GD_COST_TOL, double lambda, int MAX_GD_ITER ){
    bool b_max_iter;
    return findZero(initial_point, Jcst, gradJ, GD_GAIN, GD_COST_TOL, lambda, MAX_GD_ITER, b_max_iter );
}