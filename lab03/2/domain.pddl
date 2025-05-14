(define (domain cleaning-robot-world)
  (:requirements :strips :typing :negative-preconditions)

  (:types
    robot
    room
  )

  (:predicates
    (at ?r - robot ?p - room)
    (is_dirty ?p - room)
    (is_clean ?p - room)
    (connected ?p1 - room ?p2 - room)
  )

  (:action move
    :parameters (?r - robot ?from_room - room ?to_room - room)
    :precondition (and
                    (at ?r ?from_room)   
                    (connected ?from_room ?to_room) 
                  )
    :effect (and
              (not (at ?r ?from_room))
              (at ?r ?to_room)       
            )
  )

  (:action clean_current_room 
    :parameters (?r - robot ?p_to_clean - room)
    :precondition (and
                    (at ?r ?p_to_clean) 
                    (is_dirty ?p_to_clean)
                  )
    :effect (and
              (not (is_dirty ?p_to_clean)) 
              (is_clean ?p_to_clean)    
            )
  )
)