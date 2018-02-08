#!/usr/bin/python
'''
Builds ROS CMS scenes from a manifest file, the path to which is supplied on
the command line. This expects to be run from the ros_cms/lgiscms directory.

The manifest file should be CSV, containing a header line followed by one line
per scene. The file contains several fields per line:
    * Presentation Group, Presentation, and Scene Name are obvious
    * KML Tour is a 'KML Tour' type asset
    * KML Icon and Ground Overlay are 'Geographic data' assets, each mapped to
      all seven screens
    * Graphic types are image assets, which should be mapped to
      their respective viewport based on a supplied geometry
Asset file name columns may be emtpy, in which case we should skip that asset
for that scene.
'''

import sys, os

sys.path.append('.')
os.environ['DJANGO_SETTINGS_MODULE'] = 'lgiscms.settings'

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

from cmsapp.models import *
from django.db import transaction

import csv
import re
import uuid

class DryRun(Exception):
    pass

class SceneBuilder():
    def __init__(self, *args, **kwargs):
        self.filename = args[0]
        self.group_cache = {}
        self.presentation_cache = {}
        self.user = User.objects.first()
        self.dc = DisplayConfiguration.objects.get(slug='lgx_121')

    def get_slug(self, name):
        return '%s__%s' % (uuid.uuid4(), re.sub(r'[^0-9a-zA-Z]', '-', name).lower())

    def get_group(self, name):
        if name in self.group_cache:
            logger.info("*** *** *** *** Found group %s in cache *** *** ***" % name)
            return self.group_cache[name]

        #import code; code.interact(local=dict(globals(), **locals()))
        for g in PresentationGroup.objects.filter(name=name):
            #g = PresentationGroup.objects.get(name=name)
            # Clean out the presentation group
            for p in g.presentations.all():
                for s in p.scenes.all():
                    for a in s.assets.all():
                        a.delete()
                    s.delete()
                p.delete()
            g.delete()
        #except:
        g = PresentationGroup(name=name, description=name,slug=self.get_slug(name), active=True)
        logger.info("Created new group %s" % name)
        g.save()

        self.group_cache[name] = g
        return g

    def get_presentation(self, name, group):
        if group.name in self.presentation_cache and name in self.presentation_cache[group.name]:
            logger.info("*** *** *** *** Found presentation %s in cache *** *** ***" % name)
            return self.presentation_cache[group.name][name]

        p = Presentation(
                name=name,
                description=name,
                slug=self.get_slug(name),
                created_by=self.user,
                modified_by=self.user,
                display_configuration=self.dc)
        logger.info("Created new presentation %s" % name)
        p.save()
        last_pgm = group.presentationgroupmembership_set.order_by('sort').last()
        sort = 100
        if last_pgm:
            sort = last_pgm.sort + 10

        PresentationGroupMembership(
                presentation=p,
                group=group,
                active=True,
                touchscreen_visible=True,
                sort=sort
                ).save()

        if not group.name in self.presentation_cache:
            self.presentation_cache[group.name] = {}
        self.presentation_cache[group.name][name] = p
        return p

    def make_sxa(self, scene, asset, vp, geo, typ):
        if typ == 'Graphic' or typ == 'Browser':
            my_width = geo[0]
            my_height = geo[1]
            my_xpos = geo[2]
            my_ypos = geo[3] 
        else:
            my_width = vp.display_width
            my_height = vp.display_height
            my_xpos = 0
            my_ypos = 0 
        SceneByActivity(
                scene=scene,
                asset=asset,
                created_by=self.user,
                modified_by=self.user,
                presentation_viewport=vp,
                x_coord=my_xpos,
                y_coord=my_ypos,
                width=my_width,
                height=my_height,
                ).save()

    def make_asset(self, scene, asset_def):
        name, typ, arg = asset_def

        # Do file check stuff here
        if typ == 'Graphic':
            # Confirm file exists
            asset_file = "/media/lgmedia/ros_cms_default_assets/%s" % name 

            if not os.path.isfile(asset_file):
                return

        asset = Asset(
                name=name,
                location=name,
                slug=self.get_slug(name),
                created_by=self.user,
                modified_by=self.user,
                asset_type=AssetType.objects.get(name=typ))
        asset.save()

        if typ == 'Geographic Data' or typ == 'Panoramic Image':
            for vp in self.dc.viewports.all():
                if not vp.is_touchscreen:
                    if (
                            vp.message_identifier == 'left_three' and arg == 'left'
                        ) or (
                            vp.message_identifier == 'left_two' and arg == 'right'):
                        self.make_sxa(scene, asset, vp, None, typ)
                    elif arg == None:
                        self.make_sxa(scene, asset, vp, None, typ)
        elif typ == 'Graphic' or type == 'Browser':
            found = False
            for vp in self.dc.viewports.all():
                if not vp.is_touchscreen:
                    # Assign viewport
                    pos = re.split('[x+]',arg)
                    if ( 
                        vp.message_identifier == 'left_three' and 0 <= float(pos[2]) < 1080
                    ) or (
                        vp.message_identifier == 'left_two' and 1080 <= float(pos[2]) < 2160
                    ) or (
                        vp.message_identifier == 'left_one' and 2160 <= float(pos[2]) < 3240
                    ) or (
                        vp.message_identifier == 'center' and 3240 <= float(pos[2]) < 4320
                    ) or (
                        vp.message_identifier == 'right_one' and 4320 <= float(pos[2]) < 5400
                    ) or (
                        vp.message_identifier == 'right_two' and 5400 <= float(pos[2]) < 6480
                    ) or (
                        vp.message_identifier == 'right_three' and 6480 <= float(pos[2]) < 7560
                    ):
                        
                        self.make_sxa(scene, asset, vp, pos, typ)
                        found = True
            if found == False:
                print("Could not find proper viewport for asset")

        elif typ == 'KML Tour':
            for vp in self.dc.viewports.all():
                if vp.is_master:
                    self.make_sxa(scene, asset, vp, None,  typ)

    def make_scene(self, row):
        print row
        groupnm, presnm, scenenm, tourfile, iconfile, overlayimg, imgpos, left3kml, left2kml, dur = row
        group = self.get_group(groupnm)
        presentation = self.get_presentation(presnm, group)
        last_pm = presentation.presentationmembership_set.order_by('sort').last()
        sort = 100
        if last_pm:
            sort = last_pm.sort + 10

        scene = Scene(
                name=scenenm, slug=self.get_slug(scenenm),
                duration=int(dur),
                created_by=self.user,
                modified_by=self.user)
        scene.save()

        PresentationMembership(
                scene=scene,
                presentation=presentation,
                active=True,
                touchscreen_visible=True,
                sort=sort
                ).save()

        assets = [
                [tourfile, 'KML Tour', None],
                [iconfile, 'Geographic Data', None],
                [overlayimg, 'Graphic', imgpos ],
                [left3kml, 'Geographic Data', 'left'],
                [left2kml, 'Geographic Data', 'right']
        ]

        for a in assets:
            if a[0]:
                asset = self.make_asset(scene, a)

    def go(self):
        first = True
        with open(self.filename) as csvfile:
            scenereader = csv.reader(csvfile, delimiter=',', quotechar=None)
            for row in scenereader:
                if first:
                    first = False
                else:
                    self.make_scene(row)
            #raise DryRun('Not saving')


if __name__ == "__main__":
    with transaction.atomic():
        sb = SceneBuilder(sys.argv[1]).go()

