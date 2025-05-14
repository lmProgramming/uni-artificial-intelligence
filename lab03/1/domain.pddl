(define (domain package-transport-step6)
  (:requirements :strips :typing :negative-preconditions :action-costs 
                 :durative-actions :conditional-effects) ; Added :conditional-effects

  (:types
    package
    location
        city airport port - location
    vehicle
        truck plane ship - vehicle
  )

  (:predicates
    (at-pkg ?p - package ?l - location)
    (at-vehicle ?v - vehicle ?l - location)
    (in-pkg ?p - package ?v - vehicle)
    (road-connection ?from - location ?to - location)
    (air-connection ?from - airport ?to - airport)
    (sea-connection ?from - port ?to - port)
    (fragile ?p - package) ; New predicate for fragile packages
  )

  (:functions
    (total-cost) - number
    (travel-distance ?l1 - location ?l2 - location) - number
    (speed ?v - vehicle) - number
    (load-unload-fixed-time) - number
  )

  (:durative-action load-package
    :parameters (?pkg - package ?veh - vehicle ?loc - location)
    :duration (= ?duration (load-unload-fixed-time))
    :condition (and
                 (at start (at-pkg ?pkg ?loc))
                 (at start (at-vehicle ?veh ?loc))
               )
    :effect (and
              (at end (in-pkg ?pkg ?veh))
              (at end (not (at-pkg ?pkg ?loc)))
              ; Conditional costs
              (when (and (at start (fragile ?pkg)))  ; If fragile
                    (at end (increase (total-cost) 15))) ; Total load cost for fragile = 5 (base) + 10 (extra)
              (when (and (at start (not (fragile ?pkg)))) ; If NOT fragile (requires :negative-preconditions also for conditions in 'when')
                    (at end (increase (total-cost) 5)))   ; Base load cost
            )
  )

  (:durative-action unload-package
    :parameters (?pkg - package ?veh - vehicle ?loc - location)
    :duration (= ?duration (load-unload-fixed-time))
    :condition (and
                 (at start (in-pkg ?pkg ?veh))
                 (at start (at-vehicle ?veh ?loc))
               )
    :effect (and
              (at end (at-pkg ?pkg ?loc))
              (at end (not (in-pkg ?pkg ?veh)))
              (at end (increase (total-cost) 3))
              ; Could add conditional cost for unloading fragile items too if desired
            )
  )

  (:durative-action drive-truck
    :parameters (?tr - truck ?from - location ?to - location)
    :duration (= ?duration (/ (travel-distance ?from ?to) (speed ?tr)))
    :condition (and
                 (at start (at-vehicle ?tr ?from))
                 (over all (road-connection ?from ?to))
               )
    :effect (and
              (at start (not (at-vehicle ?tr ?from)))
              (at end (at-vehicle ?tr ?to))
              (at end (increase (total-cost) 10))
            )
  )

  (:durative-action fly-plane
    :parameters (?pl - plane ?from - airport ?to - airport)
    :duration (= ?duration (/ (travel-distance ?from ?to) (speed ?pl)))
    :condition (and
                 (at start (at-vehicle ?pl ?from))
                 (over all (air-connection ?from ?to))
               )
    :effect (and
              (at start (not (at-vehicle ?pl ?from)))
              (at end (at-vehicle ?pl ?to))
              (at end (increase (total-cost) 100))
            )
  )

  (:durative-action sail-ship
    :parameters (?sh - ship ?from - port ?to - port)
    :duration (= ?duration (/ (travel-distance ?from ?to) (speed ?sh)))
    :condition (and
                 (at start (at-vehicle ?sh ?from))
                 (over all (sea-connection ?from ?to))
               )
    :effect (and
              (at start (not (at-vehicle ?sh ?from)))
              (at end (at-vehicle ?sh ?to))
              (at end (increase (total-cost) 50))
            )
  )
)