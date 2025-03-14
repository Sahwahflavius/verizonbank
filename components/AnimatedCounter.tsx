import React from 'react'
import CountUp from 'react-countup'

const AnimatedCounter = ({amount}:{amount: number}) => {
  return (
    
      <CountUp className='w-2 font-bold'
       decimal='.'
        decimals={2}    
        start={8}
        end={amount}
        //separator=','   
        prefix='$' 
      />
    
  )
}

export default AnimatedCounter



