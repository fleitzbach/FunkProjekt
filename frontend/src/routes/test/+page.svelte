<script lang="ts">
  import Chart from 'chart.js/auto';
  import { onMount } from 'svelte';

  let chartElement;
  let chart;

  let weatherData = [
      { "season": "autumn2021", "TMAX": 11.1589197713, "TMIN": 5.0074117879 },
      { "season": "spring2021", "TMAX": 17.7811594203, "TMIN": 7.7956331045 },
      { "season": "summer2021", "TMAX": 23.3749346771, "TMIN": 13.289193729 },
      { "season": "winter2021", "TMAX": 6.3487922705, "TMIN": 0.500173913 },
      { "season": "autumn2022", "TMAX": 11.1589197713, "TMIN": 5.0074117879 },
      { "season": "spring2022", "TMAX": 17.7811594203, "TMIN": 7.7956331045 },
      { "season": "summer2022", "TMAX": 23.3749346771, "TMIN": 13.289193729 },
      { "season": "winter2022", "TMAX": 6.3487922705, "TMIN": 0.500173913 }
  ];

  onMount(() => {
      chart = new Chart(chartElement, {
          type: 'line',
          data: {
              labels: [], // Initialisiere Labels leer, werden durch updateChart gefüllt
              datasets: [
                  {
                      label: 'Maximum Temperature (°C)',
                      data: [],
                      tension: 0.2,
                      borderColor: '#ef4444'
                  },
                  {
                      label: 'Minimum Temperature (°C)',
                      data: [],
                      tension: 0.2,
                      borderColor: '#00f'
                  }
              ]
          },
          options: {
              // Deine Chart-Optionen
          }
      });

      // Aktualisiere das Chart sofort mit den vordefinierten Daten
      updateChart(weatherData);
  });

  function updateChart(data) {
      if (!chart || !data) return;

      const labels = data.map(d => {
          const seasonCode = d.season.substring(0, d.season.length - 4);
          const year = d.season.substring(d.season.length - 4);
          let season;
          switch(seasonCode) {
              case 'spring': season = 'Spring'; break;
              case 'summer': season = 'Sommer'; break;
              case 'autumn': season = 'Herbst'; break;
              case 'winter': season = 'Winter'; break;
              default: season = 'Unbekannt';
          }
          return `${season} ${year}`;
      });

      chart.data.labels = labels;
      chart.data.datasets[0].data = data.map(d => d.TMAX);
      chart.data.datasets[1].data = data.map(d => d.TMIN);
      chart.update();
  }
</script>

<div class="w-full flex flex-row bg-primary-foreground">
  <!-- Visualisation -->
  <div class="w-full min-w-0 p-5">
      <div class="relative h-full max-h-96 w-full">
          <canvas bind:this={chartElement}></canvas>
      </div>
  </div>
</div>
