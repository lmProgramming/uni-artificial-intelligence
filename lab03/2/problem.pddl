(define (problem clean-all-rooms-task-minimal)
  (:domain cleaning-robot-world)

  (:objects
    r1 - robot
    p1 - room
    p2 - room
    p3 - room
  )

  (:init
    (at r1 p1)
    (is_dirty p1)
    (is_dirty p2)
    (is_dirty p3)
    (connected p1 p2)
    (connected p2 p1)
    (connected p1 p3)
    (connected p3 p1)
  )

  (:goal
    (and
        (is_clean p1)
        (is_clean p2)
        (is_clean p3)
    )
  )
)