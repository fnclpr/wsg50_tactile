/*

    Trapez Generator Class
    This class generates a scalar trajectory w. a vel trapez profile

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

#ifndef TRAPEZ_VEL_TRAJ_H
#define TRAPEZ_VEL_TRAJ_H

#include <math.h>
#include "sun_traj_lib/Scalar_Traj_Interface.h"

namespace sun
{
//! ScalarTrajectory Traj Trapezoidal Velocity
/*!
    All input values are feasible but the interface is more complex
    \sa Trapez_Traj
*/
class Trapez_Vel_Traj : public Scalar_Traj_Interface
{
private:
  /*!
      No default Constructor
  */
  Trapez_Vel_Traj();

protected:
  /*!
      initial position, acceleration, cruise time, cruise duration
  */
  double _pi, _ddp, _tc, _tv;

public:
  /*=======CONSTRUCTORS======*/

  /*!
      Constructor
  */
  Trapez_Vel_Traj(

      double cruise_speed, double cruise_duration, double acceleration, double initial_position = 0.0,
      double initial_time = 0.0);

  /*!
      Copy Constructor
  */
  Trapez_Vel_Traj(const Trapez_Vel_Traj& traj) = default;

  /*!
      Clone the object in the heap
  */
  virtual Trapez_Vel_Traj* clone() const override;

  /*=======END CONSTRUCTORS======*/

  /*======= GETTERS =========*/

  virtual double getFinalPosition() const;

  double getCruiseTime() const;

  /*======= END GETTERS =========*/

  /*======SETTERS==========*/

  /*======END SETTERS==========*/

  /*!
      Get Position at time secs
  */
  virtual double getPosition(double secs) const override;

  /*!
      Get Velocity at time secs
  */
  virtual double getVelocity(double secs) const override;

  /*!
      Get Acceleration at time secs
  */
  virtual double getAcceleration(double secs) const override;

};  // END CLASS Quintic_Poly_Traj

using Trapez_Vel_Traj_Ptr = std::unique_ptr<Trapez_Vel_Traj>;

}  // namespace sun

#endif