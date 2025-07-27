from django.shortcuts import render, get_object_or_404, redirect
from .models import ChatSession, Message
from users.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

@login_required
def chat_dashboard(request, user_id=None):
    query = request.GET.get('search', '')
    current_user = request.user
    
    # Get contacts based on user role
    if current_user.role.lower() == 'admin':
        # Admin can chat with everyone (farmers and vets)
        contacts = User.objects.filter(
            Q(role__iexact='FARMER') | Q(role__iexact='VET')
        ).exclude(id=current_user.id)
    elif current_user.role.lower() == 'farmer':
        # Farmers can chat with vets and admins
        contacts = User.objects.filter(
            Q(role__iexact='VET') | Q(role__iexact='ADMIN')
        ).exclude(id=current_user.id)
    elif current_user.role.lower() == 'vet':
        # Vets can chat with farmers and admins
        contacts = User.objects.filter(
            Q(role__iexact='FARMER') | Q(role__iexact='ADMIN')
        ).exclude(id=current_user.id)
    else:
        contacts = User.objects.none()

    # Get existing chats
    chats = ChatSession.objects.filter(
        Q(sender=current_user) | Q(receiver=current_user)
    ).distinct().order_by('-last_updated')

    # Add partner information to chats
    for chat in chats:
        chat.partner = chat.receiver if chat.sender == current_user else chat.sender
        # Get last message for preview
        last_message = Message.objects.filter(chat=chat).order_by('-timestamp').first()
        chat.last_message = last_message.content[:50] + "..." if last_message and last_message.content else "No messages yet"
    
    # Handle specific user chat
    selected_chat = None
    messages = None
    other_user = None

    if user_id:
        other_user = get_object_or_404(User, id=user_id)
        
        # Create or get chat session
        chat, created = ChatSession.objects.get_or_create(
            sender=min(current_user, other_user, key=lambda x: x.id),
            receiver=max(current_user, other_user, key=lambda x: x.id)
        )
        selected_chat = chat

        # Handle message posting
        if request.method == 'POST':
            content = request.POST.get('content', '').strip()
            attachment = request.FILES.get('attachment')

            if content or attachment:
                Message.objects.create(
                    chat=chat,
                    sender=current_user,
                    content=content,
                    attachment=attachment
                )
                # Update chat timestamp
                chat.save()
            return redirect('chat:open_chat', user_id=other_user.id)

        messages = Message.objects.filter(chat=chat).order_by('timestamp')

    # Apply search filter if query exists
    if query:
        contacts = contacts.filter(
            Q(username__icontains=query) | 
            Q(first_name__icontains=query) | 
            Q(last_name__icontains=query)
        )

    # Separate contacts by role for display
    farmers = contacts.filter(role__iexact='FARMER')
    vets = contacts.filter(role__iexact='VET') 
    admins = contacts.filter(role__iexact='ADMIN')

    return render(request, 'chat/dashboard.html', {
        'ongoing_chats': chats,
        'farmers': farmers,
        'vets': vets,
        'admins': admins,
        'contacts': contacts,
        'selected_chat': selected_chat,
        'messages': messages,
        'other_user': other_user,
    })