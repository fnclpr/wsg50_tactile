/*

    Quintic Poly Generator Class
    This class generates a scalar trajectory w. a quintic poly

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

#ifndef QUINTIC_POLY_TRAJ_H
#define QUINTIC_POLY_TRAJ_H

#include "sun_math_toolbox/GeometryHelper.h"
#include "sun_traj_lib/Scalar_Traj_Interface.h"

#define QUINTIC_POLY_EPS_TIME 0.001

namespace sun
{
//! Scalar trajectory implemented as a Quintic Poly
class Quintic_Poly_Traj : public Scalar_Traj_Interface
{
private:
  /*!
      No default Constructor
  */
  Quintic_Poly_Traj();

protected:
  /*!
      Poly coeff of p(t)
  */
  TooN::Vector<6> _poly_coeff;

  /*!
      Poly coeff of dp(t)
  */
  TooN::Vector<5> _vel_poly_coeff;

  /*!
      Poly coeff of ddp(t)
  */
  TooN::Vector<4> _acc_poly_coeff;

  /*
      initial position, final position
      initial velocity, final velocity
      initial acceleration, final acceleration
  */
  double _pi, _pf, _vi, _vf, _aci, _acf;

public:
  /*=======CONSTRUCTORS======*/

  /*!
      Constructor
  */
  Quintic_Poly_Traj(double duration, double initial_position, double final_position, double initial_time = 0.0,
                    double initial_velocity = 0.0, double final_velocity = 0.0, double initial_acceleration = 0.0,
                    double final_acceleration = 0.0);

  /*!
      Copy Constructor
  */
  Quintic_Poly_Traj(const Quintic_Poly_Traj& quint) = default;

  /*!
      Clone the object in the heap
  */
  virtual Quintic_Poly_Traj* clone() const override;

  /*=======END CONSTRUCTORS======*/

  /*======= GETTERS =========*/

  virtual double getInitialPosition() const;

  virtual double getFinalPosition() const;

  virtual double getInitialVelocity() const;

  virtual double getFinalVelocity() const;

  virtual double getInitialAcceleration() const;

  virtual double getFinalAcceleration() const;

  /*======= END GETTERS =========*/

  /*======SETTERS==========*/

  virtual void setInitialPosition(double pi);

  virtual void setFinalPosition(double pf);

  virtual void setInitialVelocity(double vi);

  virtual void setFinalVelocity(double vf);

  virtual void setInitialAcceleration(double ai);

  virtual void setFinalAcceleration(double af);

  /*!
      Change the initial time instant (translate the trajectory in the time)
  */
  virtual void changeInitialTime(double initial_time) override;

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

  /*!
      Update poly coefficients
  */
  virtual void updateCoefficients();

};  // END CLASS Quintic_Poly_Traj

using Quintic_Poly_Traj_Ptr = std::unique_ptr<Quintic_Poly_Traj>;

}  // namespace sun

#endif