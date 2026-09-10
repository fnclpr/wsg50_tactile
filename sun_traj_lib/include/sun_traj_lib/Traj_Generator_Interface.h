/*

    Trajectory Generator Interface Class
    This class is a general interface to trajectory generators classes

    Copyright 2018-2020 Università della Campania Luigi Vanvitelli

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

#ifndef TRAJ_GEN_INTERFACE_H
#define TRAJ_GEN_INTERFACE_H

#include <iostream>
#include <memory>

#define TRAJ_ERROR_COLOR "\033[1m\033[31m" /* Bold Red */
#define TRAJ_WARN_COLOR "\033[1m\033[33m"  /* Bold Yellow */
#ifndef CRESET
#define CRESET "\033[0m"
#endif

namespace sun
{
//! General Interface for all traj generators
class Traj_Generator_Interface
{
private:
  /*!
      No default Constructor
  */
  Traj_Generator_Interface();

protected:
  /*!
      initial time of the trajectory
  */
  double _initial_time;

  /*!
      final time of the trajectory
  */
  double _final_time;

public:
  /*======CONSTRUCTORS=========*/

  /*!
      Constructor with duration and initial time as input
  */
  Traj_Generator_Interface(double duration, double initial_time = 0.0) : _initial_time(initial_time)
  {
    if (duration < 0.0)
    {
      std::cout << TRAJ_ERROR_COLOR "Error in Traj_Generator_Interface( double duration, double initial_time) duration "
                                    "has to be >= 0" CRESET
                << std::endl;
      exit(-1);
    }
    _final_time = _initial_time + duration;
  }

  // Traj_Generator_Interface( const Traj_Generator_Interface& traj );

  /*!
      Clone the object in the heap
  */
  virtual Traj_Generator_Interface* clone() const = 0;

  /*======END CONSTRUCTORS=========*/

  /*====== GETTERS =========*/

  /*!
      Get the final time instant
  */
  virtual double getFinalTime() const
  {
    return _final_time;
  }

  /*!
      Get the initial time instant
  */
  virtual double getInitialTime() const
  {
    return _initial_time;
  }

  /*!
      Get the duration
  */
  virtual double getDuration() const
  {
    return getFinalTime() - getInitialTime();
  }

  /*!
      Get the time left
  */
  virtual double getTimeLeft(double secs) const
  {
    return (getFinalTime() - secs);
  }

  /*====== END GETTERS =========*/

  /*====== SETTERS =========*/

  /*!
      Change the initial time instant (translate the trajectory in the time)
  */
  virtual void changeInitialTime(double initial_time)
  {
    _final_time = initial_time + getDuration();
    _initial_time = initial_time;
  }

  /*====== END SETTERS =========*/

  /*!
      return true if the trajectory is compleate at time secs
  */
  virtual bool isCompleate(double secs) const
  {
    return (secs >= getFinalTime());
  }

  /*!
      return true if the trajectory is started at time secs
  */
  virtual bool isStarted(double secs) const
  {
    return (secs >= getInitialTime());
  }

};  // END CLASS Traj_Generator_Interface

using Traj_Generator_Interface_Ptr = std::unique_ptr<Traj_Generator_Interface>;

}  // namespace sun

#endif