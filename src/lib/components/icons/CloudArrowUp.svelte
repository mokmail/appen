<script lang="ts">
	import CloudUpload from 'lucide-svelte/icons/cloud-upload';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<CloudUpload
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
