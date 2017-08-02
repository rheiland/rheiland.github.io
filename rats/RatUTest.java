package main;

import grid.Location;
import actor.RatBot;
import actor.RatBotActor;

/**
 * 
 * 
 * @author workstation
 * Note on direction: 0 = North, 90 = East, 180 = South, 360 = West
 * 
 * output:
   movingOntoTail: (10, 23)
   blockAhead: (10, 23)
 */
public class RatUTest extends RatBot
{ 
	
	public RatUTest()
    {
        this.setName("RatUTest");
    }
	
	@Override
	public void initForRound()
    {
        setDesiredHeading(90);  // let's just travel east
    }
	
	@Override
	public int chooseAction()
	{
//		System.out.println("for loc="+getLocation() + ", getNeighbors= " + getSensorGrid().getNeighbors(getLocation()));
//		System.out.println(" getOccupiedLocations= " + getSensorGrid().getOccupiedLocations());
	
		Location loc = getLocation().getAdjacentLocation(getDesiredHeading());
		System.out.println("   loc 1 ahead= " + loc);
		RatBotActor a1 = getSensorGrid().get(loc);
		System.out.println("----     a1= " + a1);
        
		Location loc2 = getLocation().getAdjacentLocation(getDesiredHeading()).getAdjacentLocation(getDesiredHeading());
		System.out.println("---------   loc 2 ahead= " + loc2);
		RatBotActor a2 = getSensorGrid().get(loc2);
		System.out.println("---------     a2= " + a2);
        
        // Trying the following doesn't work either
//        setLocation(loc2);
//        System.out.println("after setLocation=loc2,  canMove()= " + canMove());
        
        return MOVE;
    }
}