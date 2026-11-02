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

#ifndef LEARN_ALGS_LIB_H
#define LEARN_ALGS_LIB_H

#include <cmath>
#include <boost/function.hpp>

double findZero(double initial_point, const boost::function<double(double)>& Jcst, const boost::function<double(double)>& gradJ, double GD_GAIN, double GD_COST_TOL, double lambda, int MAX_GD_ITER );

double findZero(double initial_point, const boost::function<double(double)>& Jcst, const boost::function<double(double)>& gradJ, double GD_GAIN, double GD_COST_TOL, double lambda, int MAX_GD_ITER, bool& b_max_iter );

#endif