<script lang="ts">
	import Calendar from 'lucide-svelte/icons/calendar';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<Calendar
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
