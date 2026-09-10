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

#ifndef TRAPEZ_TRAJ_H
#define TRAPEZ_TRAJ_H

#include <math.h>
#include "sun_traj_lib/Scalar_Traj_Interface.h"

namespace sun
{
//! ScalarTrajectory Traj Trapezoidal Velocity
/*!
    This implementation needs feasible values as input
    \sa Trapez_Vel_Traj
*/
class Trapez_Traj : public Scalar_Traj_Interface
{
private:
  /*!
      No default Constructor
  */
  Trapez_Traj();

protected:
  /*
      initial position, final position
      cruise time
  */
  double _pi, _pf, _tc;
  double _ddp;

public:
  static bool checkTrapez(double duration, double initial_position, double final_position, double cruise_speed);

  /*=======CONSTRUCTORS======*/

  /*!
      Constructor
  */
  Trapez_Traj(double duration, double initial_position, double final_position, double cruise_speed,
              double initial_time = 0.0);

  /*!
      Copy Constructor
  */
  Trapez_Traj(const Trapez_Traj& quint) = default;

  /*!
      Clone the object in the heap
  */
  virtual Trapez_Traj* clone() const override;

  /*=======END CONSTRUCTORS======*/

  /*======= GETTERS =========*/

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

using Trapez_Traj_Ptr = std::unique_ptr<Trapez_Traj>;

}  // namespace sun

#endif