/*

    Vector Independent Traj Class
    This class generates a vector trajectory basing on independent scalar
   trajectories

    Copyright 2019-2020 Università della Campania Luigi Vanvitelli

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

#include <sun_traj_lib/Vector_Independent_Traj.h>

using namespace TooN;

namespace sun
{
/* ====== CONSTRUCTORS =======*/

/*
    Void Constructor
*/
Vector_Independent_Traj::Vector_Independent_Traj() : Vector_Traj_Interface(NAN, NAN)
{
}

/*
    Full constructor
*/
Vector_Independent_Traj::Vector_Independent_Traj(const std::vector<Scalar_Traj_Interface_Ptr> &traj_vec)
  : Vector_Traj_Interface(NAN, NAN)
{
  for (const auto &element : traj_vec)
  {
    _traj_vec.push_back(Scalar_Traj_Interface_Ptr(element->clone()));
  }
}

/*
    Constructor that creates n equal trajectories
*/
Vector_Independent_Traj::Vector_Independent_Traj(const Scalar_Traj_Interface &traj, int n)
  : Vector_Traj_Interface(NAN, NAN)
{
  for (int i = 0; i < n; i++)
  {
    _traj_vec.push_back(Scalar_Traj_Interface_Ptr(traj.clone()));
  }
}

/*
    Copy Constructor
*/
Vector_Independent_Traj::Vector_Independent_Traj(const Vector_Independent_Traj &traj) : Vector_Traj_Interface(traj)
{
  _initial_time = NAN;
  _final_time = NAN;
  // Clone traj
  for (const auto &element : traj._traj_vec)
  {
    _traj_vec.push_back(Scalar_Traj_Interface_Ptr(element->clone()));
  }
}

/*
    Clone the object in the heap
*/
Vector_Independent_Traj *Vector_Independent_Traj::clone() const
{
  return new Vector_Independent_Traj(*this);
}

/* ====== END CONSTRUCTORS =======*/

/* ====== SETTERS =========*/

/*
    Push back a trajectory in the vector
*/
void Vector_Independent_Traj::push_back_traj(const Scalar_Traj_Interface &traj)
{
  _traj_vec.push_back(Scalar_Traj_Interface_Ptr(traj.clone()));
}

/*
    Remove last traj of the vector
*/
void Vector_Independent_Traj::pop_back_traj()
{
  _traj_vec.pop_back();
}

/* ====== END SETTERS =========*/

/*====== GETTERS =========*/

/*
    get size of the vector
*/
int Vector_Independent_Traj::size() const
{
  return _traj_vec.size();
}

/*
    Get the final time instant
    It is the max final time
*/
double Vector_Independent_Traj::getFinalTime() const
{
  double final_time = -INFINITY;
  for (const auto &element : _traj_vec)
  {
    double ith_final_time = element->getFinalTime();
    if (ith_final_time > final_time)
      final_time = ith_final_time;
  }
  return final_time;
}

/*
    Get the initial time instant
    It is the min initial time
*/
double Vector_Independent_Traj::getInitialTime() const
{
  double initial_time = INFINITY;
  for (const auto &element : _traj_vec)
  {
    double ith_initial_time = element->getInitialTime();
    if (ith_initial_time < initial_time)
      initial_time = ith_initial_time;
  }
  return initial_time;
}

/*====== END GETTERS =========*/

/*====== SETTERS =========*/

/*
    Change the initial time instant (translate all the trajectories in the time)
*/
void Vector_Independent_Traj::changeInitialTime(double initial_time)
{
  double previous_initial_time = getInitialTime();
  double Delta_T = previous_initial_time - initial_time;
  for (auto &element : _traj_vec)
  {
    element->changeInitialTime(element->getInitialTime() - Delta_T);
  }
}

/*====== END SETTERS =========*/

/*
    return true if all the trajectories are compleate at time secs
*/
bool Vector_Independent_Traj::isCompleate(double secs) const
{
  for (const auto &element : _traj_vec)
  {
    if (!element->isCompleate(secs))
      return false;
  }
  return true;
}

/*
    return true if the at least one trajectory is started at time secs
*/
bool Vector_Independent_Traj::isStarted(double secs) const
{
  for (const auto &element : _traj_vec)
  {
    if (element->isStarted(secs))
      return true;
  }
  return false;
}

/*====== RUNNERS =========*/

/*
    Get Position at time secs
*/
Vector<> Vector_Independent_Traj::getPosition(double secs) const
{
  Vector<> out = NAN * Ones(_traj_vec.size());
  for (int i = 0; i < _traj_vec.size(); i++)
  {
    out[i] = _traj_vec[i]->getPosition(secs);
  }
  return out;
}

/*
    Get Velocity at time secs
*/
Vector<> Vector_Independent_Traj::getVelocity(double secs) const
{
  Vector<> out = NAN * Ones(_traj_vec.size());
  for (int i = 0; i < _traj_vec.size(); i++)
  {
    out[i] = _traj_vec[i]->getVelocity(secs);
  }
  return out;
}

/*
    Get Acceleration at time secs
*/
Vector<> Vector_Independent_Traj::getAcceleration(double secs) const
{
  Vector<> out = NAN * Ones(_traj_vec.size());
  for (int i = 0; i < _traj_vec.size(); i++)
  {
    out[i] = _traj_vec[i]->getAcceleration(secs);
  }
  return out;
}

/*====== END RUNNERS =========*/

}  // namespace sun
