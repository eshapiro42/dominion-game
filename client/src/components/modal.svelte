<script>
    export let show = false;
</script>

{#if show}
    <main
        on:click|self
    >
        <div class="contents">
            <slot name="contents">
                <span class="missing"></span>
            </slot>
        </div>
    </main>
{/if}

<style>
    main {
        width: 100%;
        height: 100%;
        left: 0;
        top: 0;
        display: flex;
        position: fixed;
        background-color: rgba(0, 0, 0, 0.7);
        text-align: center;
        z-index: 10;
    }

    .contents {
        justify-content: center;
        align-items: center;
        margin: auto;
    }
</style>