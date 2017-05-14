
function! taskwarrior#preview(context, task) abort
	if a:context.vertical_preview
		let denite_winwidth = &columns
		pclose!
		silent vnew
	else
		let previewheight_save = &previewheight
		try
			let &previewheight = a:context.previewheight
			silent new
		finally
			let &previewheight = previewheight_save
		endtry
	endif
	setlocal previewwindow
	setlocal bufhidden=delete
	setlocal buftype=nofile
	call s:window_opts()
	call s:highlights()
	call append(0, a:task)
	setlocal readonly
	setlocal nomodifiable
	1
	execute 'vert resize ' . (denite_winwidth / 2)
	wincmd p
endfunction

function! taskwarrior#edit(context, task) abort
	let filename = tempname().'.taskedit'
	call writefile(a:task, filename)

	execute 'silent! edit '.filename
	call s:window_opts()
	call s:highlights()

	" TODO: Edit capabilities
	" autocmd taskwarrior-edit BufWritePost *.taskedit

	" Clear 'write' event when buffer is deleted
	" autocmd taskwarrior-edit BufDelete *.taskedit
	" 	\ autocmd! taskwarrior-edit BufWritePost
endfunction

function! s:window_opts() abort
	setlocal noswapfile
	setlocal syntax=none
	setlocal filetype=taskedit

	nnoremap <silent> <buffer> q :<C-u>bdelete<CR>
endfunction

function! s:highlights() abort
	syntax match taskeditHeading "^\s*#\s*Name\s\+Details\s*$" contained
endfunction

" augroup taskwarrior-edit
" 	autocmd!
" augroup END
