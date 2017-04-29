#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2017 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""
Removes all the created entities from the database so we can test an import from scratch.
"""

from perks import db, models


def delete_all(objects):
    for obj in objects:
        db.session.delete(obj)


def main():  # NOQA
    print 'removing elections'
    delete_all(models.Election.query.all())
    print 'removing enrollments'
    delete_all(models.Enrollment.query.all())
    print 'removing enrollment periods'
    delete_all(models.EnrollmentPeriod.query.all())
    print 'removing premiums'
    delete_all(models.PlanTierPremium.query.all())
    print 'removing supplemental plans'
    delete_all(models.OtherPlan.query.all())
    delete_all(models.CriticalIllnessPlan.query.all())
    delete_all(models.CancerPlan.query.all())
    delete_all(models.LongTermCarePlan.query.all())
    delete_all(models.SupplumentalInsurancePlan.query.all())
    print 'removing group plans'
    delete_all(models.Employee401KPlan.query.all())
    delete_all(models.HSAPlan.query.all())
    delete_all(models.ParkingTransitPlan.query.all())
    delete_all(models.FSAPlan.query.all())
    delete_all(models.LifeADDDependentPlan.query.all())
    delete_all(models.LifeADDPlan.query.all())
    delete_all(models.STDPlan.query.all())
    delete_all(models.LTDPlan.query.all())
    delete_all(models.EAPPlan.query.all())
    print 'removing core plans'
    delete_all(models.VisionPlan.query.all())
    delete_all(models.DentalPlan.query.all())
    delete_all(models.MedicalPlan.query.all())
    delete_all(models.MedicalDentalVisionBundlePlan.query.all())
    delete_all(models.MedicalDentalBundlePlan.query.all())
    delete_all(models.MedicalVisionBundlePlan.query.all())
    delete_all(models.DentalVisionBundlePlan.query.all())
    print 'removing employees'
    delete_all(models.Employee.query.all())
    print 'removing admins'
    delete_all(models.User.query.filter(models.User.username != 'admin'))
    print 'removing locations'
    delete_all(models.Location.query.all())
    print 'removing carriers'
    delete_all(models.Carrier.query.all())
    db.session.commit()


if __name__ == '__main__':
    main()
