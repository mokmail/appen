<script lang="ts">
	import KeyRound from 'lucide-svelte/icons/key-round';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<KeyRound
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
