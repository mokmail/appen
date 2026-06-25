<script lang="ts">
	import UserPlus from 'lucide-svelte/icons/user-plus';
	export let className = 'size-4';
	export let strokeWidth = '1.5';
</script>

<UserPlus
	aria-hidden="true"
	class={className}
	strokeWidth={strokeWidth}
	size={undefined}
/>
