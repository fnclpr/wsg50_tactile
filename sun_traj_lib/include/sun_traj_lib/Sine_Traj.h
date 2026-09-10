/*

    Sine Generator Class
    This class generates a scalar trajectory w. sine wave

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

#ifndef SINE_TRAJ_H
#define SINE_TRAJ_H

#include "sun_traj_lib/Scalar_Traj_Interface.h"

namespace sun
{
//! Scalar Sinusoidal trajectory
class Sine_Traj : public Scalar_Traj_Interface
{
private:
  /*!
      No default Constructor
  */
  Sine_Traj();

protected:
  /*!
      amplitude, pulse, phase, bias
  */
  double _A, _pulse, _phi, _bias;

public:
  /*=======CONSTRUCTORS======*/

  /*!
      Constructor
  */
  Sine_Traj(double duration, double amplitude, double frequency, double bias = 0.0, double phase = 0.0,
            double initial_time = 0.0);

  /*!
      Copy Constructor
  */
  Sine_Traj(const Sine_Traj& quint) = default;

  /*!
      Clone the object in the heap
  */
  virtual Sine_Traj* clone() const override;

  /*=======END CONSTRUCTORS======*/

  /*======= GETTERS =========*/

  /*======= END GETTERS =========*/

  /*======SETTERS==========*/

  /*
      Change the initial time instant (translate the trajectory in the time)
      FROM BASE CLASS
  */
  // virtual void changeInitialTime(double initial_time) override;

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

};  // END CLASS Sine_Traj

using Sine_Traj_Ptr = std::unique_ptr<Sine_Traj>;

}  // namespace sun

#endif