<script lang="ts">
	import AudioLines from 'lucide-svelte/icons/audio-lines';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<AudioLines
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
