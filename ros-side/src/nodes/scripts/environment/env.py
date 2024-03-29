#!/usr/bin/env python2

import rospy
from std_msgs.msg import String

import sys
import random
import json

import pygame
import pymunk
from pymunk import pygame_util


def init_ros(env_name):
	rospy.init_node('env', anonymous=True)

	world_pub = rospy.Publisher(env_name + '/world_properties', String, queue_size=3)

	rate = rospy.Rate(50)  # 10hz - 10 times per second

	return world_pub, rate


def add_ball(space):
	mass = 1
	radius = 14

	moment = pymunk.moment_for_circle(mass, 0, radius)
	body = pymunk.Body(mass, moment)

	x = random.randint(160, 380)
	body.position = (x, 550)
	shape = pymunk.Circle(body, radius)
	shape.friction = 0.5

	space.add(body, shape)

	return shape


def add_static_l(space):
	body = pymunk.Body(body_type=pymunk.Body.STATIC)
	body.position = (300, 300)

	l1 = pymunk.Segment(body, (-150, 0), (150, 0), 5)
	l2 = pymunk.Segment(body, (-150, 0), (-150, 50), 5)
	l3 = pymunk.Segment(body, (150, 0), (150, 50), 5)

	d_l1 = {'x': l1.body.position.x, 'y': l1.body.position.y, 'id': 2, 'w': 300, 'h': 5, 'a': 0}
	d_l2 = {'x': l2.body.position.x - 150, 'y': l2.body.position.y, 'id': 2, 'w': 5, 'h': 50, 'a': 0}
	d_l3 = {'x': l3.body.position.x + 150, 'y': l3.body.position.y, 'id': 2, 'w': 5, 'h': 50, 'a': 0}

	space.add(l1, l2, l3)

	return d_l1, d_l2, d_l3


def publish_world(publisher, statics_l, balls):
	world_list = []

	for ball in balls:
		ball_dir = {'x': ball.body.position.x, 'y': ball.body.position.y, 'r': ball.radius, 'id': 1, 'a': ball.body.angle}
		world_list.append(ball_dir)

	world_list.extend(statics_l)

	world_dir = {'properties': world_list}
	world_json = json.dumps(world_dir)
	publisher.publish(world_json)


def pymunk_run(world_pub, rate):
		# pygame.init()
		# screen = pygame.display.set_mode((600, 600))
		# pygame.display.set_caption("Joints. Just wait and the L will tip over")
		clock = pygame.time.Clock()

		space = pymunk.Space()
		space.gravity = (0.0, -900.0)

		statics_l = add_static_l(space)

		balls = []

		# draw_options = pygame_util.DrawOptions(screen)

		ticks_to_next_ball = 10

		while not rospy.is_shutdown():
			ticks_to_next_ball -= 1
			if ticks_to_next_ball <= 0:
				ticks_to_next_ball = 25
				ball_shape = add_ball(space)
				balls.append(ball_shape)

			balls_to_remove = []
			for ball in balls:
				if ball.body.position.y < 0:
					balls_to_remove.append(ball)

			for ball in balls_to_remove:
				space.remove(ball, ball.body)
				balls.remove(ball)

			space.step(1 / 50.0)

			# screen.fill((255, 255, 255))
			# space.debug_draw(draw_options)

			# pygame.display.flip()

			publish_world(publisher=world_pub, statics_l=statics_l, balls=balls)

			rate.sleep()


if __name__ == '__main__':
	try:
		world_pub, rate = init_ros(sys.argv[1])
		pymunk_run(world_pub, rate)
	except rospy.ROSInterruptException:
		pass
