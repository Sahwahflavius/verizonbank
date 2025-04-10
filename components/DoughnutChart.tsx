import React from 'react'
import { Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS,ArcElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(ArcElement, Tooltip, Legend);


const DoughnutChart = ({accounts}:DoughnutChartProps) => {
    const data = {
        datasets: [ 
            {
            label:'banks',
            data: [1500, 2000, 2500],
            backgroundColor: [
                'rgba(255, 99, 132, 12)',
                'rgba(50, 162, 217, 12)',
                'rgba(255, 206, 86, 16)'
            ],
          
        }],
        labels: ['Bank A', 'Bank B', 'Bank C']  
    };
  return <Doughnut data={data}
    options={{
        cutout: '60%',
        plugins: {
            legend: {
                display:false,
            },


        }
    }}  
  />;
}

export default DoughnutChart
