<script lang="ts">
	import Chart from 'chart.js/auto';
	import { onMount } from 'svelte';
	import { dataStore, currentStation, dataSettings } from './store';
	import { Input } from './components/ui/input';
	import { Button } from './components/ui/button';
	import { API_URL } from '../config';
	import * as Select from './components/ui/select';
	import { Label } from './components/ui/label';
	import { DateField } from './components/ui/date-field';
	import { Root } from 'postcss';
	import type { DataSettings } from './types';
	import { each } from 'chart.js/helpers';
	import * as Tooltip from "$lib/components/ui/tooltip";
	import { X } from 'lucide-svelte';
	import { LucideArrowUpRightSquare } from 'lucide-svelte';
	import { toast } from 'svelte-sonner';
	import LoadingOverlay from './loadingOverlay.svelte';
	import 'chartjs-adapter-luxon';
	import * as Sheet from "$lib/components/ui/sheet";
	import StationTable from '$lib/Datatable.svelte';
onMount(() => {
  // Init empty chart
  chart = new Chart(chartElement, {
    type: 'line',
    data: {
      labels: [],
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
      responsive: true,
      maintainAspectRatio: false,
      animation: false,
      interaction: {
        mode: 'index',
        intersect: false
      },
      plugins: {
        decimation: {
          enabled: true,
          algorithm: 'lttb',
          samples: 0.5
        }
      },
      scales: {
        x: {
          type: 'time',
          
        },
      }
    }
  });
</script>