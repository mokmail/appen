<script lang="ts">
	import EyeOff from 'lucide-svelte/icons/eye-off';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<EyeOff
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
