(define (problem multi-modal-transport-conditional)
  (:domain package-transport-step6)

  (:objects
    p1 - package
    p2 - package

    london paris newyork - city
    heathrow jfk charlesdegaulle - airport
    dover calais newyork_port - port

    my_truck - truck
    my_plane - plane
    my_ship - ship
    another_truck - truck
  )

  (:init
    (= (total-cost) 0)
    (= (load-unload-fixed-time) 1)

    (= (speed my_truck) 60)
    (= (speed another_truck) 60)
    (= (speed my_plane) 500)
    (= (speed my_ship) 30)

    (= (travel-distance london heathrow) 30) (= (travel-distance heathrow london) 30)
    (= (travel-distance london dover) 80) (= (travel-distance dover london) 80)
    (= (travel-distance paris charlesdegaulle) 20) (= (travel-distance charlesdegaulle paris) 20)
    (= (travel-distance paris calais) 150) (= (travel-distance calais paris) 150)
    (= (travel-distance newyork jfk) 25) (= (travel-distance jfk newyork) 25)
    (= (travel-distance newyork newyork_port) 10) (= (travel-distance newyork_port newyork) 10)
    (= (travel-distance jfk newyork_port) 30) (= (travel-distance newyork_port jfk) 30)
    (= (travel-distance london paris) 350) (= (travel-distance paris london) 350)
    (= (travel-distance heathrow jfk) 3000) (= (travel-distance jfk heathrow) 3000)
    (= (travel-distance heathrow charlesdegaulle) 300) (= (travel-distance charlesdegaulle heathrow) 300)
    (= (travel-distance dover calais) 50) (= (travel-distance calais dover) 50)
    (= (travel-distance calais newyork_port) 3500) (= (travel-distance newyork_port calais) 3500)

    (at-pkg p1 london)
    (fragile p1)
    
    (at-pkg p2 jfk)

    (at-vehicle my_truck london)
    (at-vehicle my_plane heathrow)
    (at-vehicle my_ship dover)
    (at-vehicle another_truck newyork_port) 

    (road-connection london heathrow) (road-connection heathrow london)
    (road-connection london dover) (road-connection dover london)
    (road-connection paris charlesdegaulle) (road-connection charlesdegaulle paris)
    (road-connection paris calais) (road-connection calais paris)
    (road-connection newyork jfk) (road-connection jfk newyork)
    (road-connection newyork newyork_port) (road-connection newyork_port newyork)
    (road-connection jfk newyork_port) (road-connection newyork_port jfk)
    (road-connection london paris) (road-connection paris london)

    (air-connection heathrow jfk) (air-connection jfk heathrow)
    (air-connection heathrow charlesdegaulle) (air-connection charlesdegaulle heathrow)

    (sea-connection dover calais) (sea-connection calais dover)
    (sea-connection calais newyork_port) (sea-connection newyork_port calais)
  )

  (:goal
    (and
        (at-pkg p1 newyork)
        (at-pkg p2 calais)
    )
  )

  (:metric minimize (total-cost)) 
)