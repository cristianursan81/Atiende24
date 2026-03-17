<?php
/**
 * ChatGenie Widget for LinkEvolution Website
 * Easy PHP integration for WordPress and other PHP-based websites
 * 
 * Usage:
 * 1. Place this file in your website directory
 * 2. Include it in your template files: <?php include 'chatgenie-widget.php'; ?>
 * 3. Or call it directly: chatgenie_render_widget();
 */

function chatgenie_render_widget($options = []) {
    // Default configuration for LinkEvolution
    $default_config = [
        'businessId' => '1', // Replace with actual business ID
        'apiKey' => 'your-api-key-here', // Replace with actual API key
        'apiBaseUrl' => 'https://your-domain.com', // Replace with your ChatGenie API URL
        'branding' => [
            'businessName' => 'LinkEvolution',
            'primaryColor' => '#667eea',
            'secondaryColor' => '#764ba2',
            'accentColor' => '#FFD700',
            'logo' => 'https://www.linkevolution.eu/images/logo.png' // Update with actual logo URL
        ],
        'template' => 'digital_transformation',
        'language' => 'es-ES',
        'position' => 'bottom-right',
        'enableVoice' => true,
        'enableDragging' => true,
        'showQuickActions' => true,
        'greeting' => "¡Hola! Soy el asistente de LinkEvolution. ¿Cómo puedo ayudarte con tu transformación digital?",
        'quickActions' => [
            ['text' => '🚀 Transformación Digital', 'message' => 'Quiero información sobre transformación digital', 'action' => 'digital_transformation'],
            ['text' => '⚡ Automatización', 'message' => 'Me interesa automatizar procesos', 'action' => 'automation'],
            ['text' => '📊 Gestión de Flujos', 'message' => 'Necesito ayuda con gestión de flujos de trabajo', 'action' => 'workflow_management'],
            ['text' => '💼 Consultoría', 'message' => 'Quiero una consultoría personalizada', 'action' => 'consultation'],
            ['text' => '📞 Contactar', 'message' => 'Quiero hablar con un consultor', 'action' => 'contact'],
            ['text' => '💰 Presupuesto', 'message' => 'Necesito un presupuesto', 'action' => 'quote']
        ],
        'leadCapture' => [
            'enabled' => true,
            'triggers' => [
                'presupuesto', 'precio', 'coste', 'consultoría', 'reunión', 'contactar',
                'transformación digital', 'automatización', 'contacto', 'información',
                'demo', 'prueba', 'análisis', 'audit', 'evaluación'
            ]
        ],
        'businessHours' => [
            'timezone' => 'Europe/Madrid',
            'monday' => ['open' => '09:00', 'close' => '19:00'],
            'tuesday' => ['open' => '09:00', 'close' => '19:00'],
            'wednesday' => ['open' => '09:00', 'close' => '19:00'],
            'thursday' => ['open' => '09:00', 'close' => '19:00'],
            'friday' => ['open' => '09:00', 'close' => '18:00'],
            'afterHoursMessage' => 'Estamos fuera del horario de atención. Déjanos tu consulta y te contactaremos pronto. También puedes llamarnos al +34 647 027 418 o escribirnos por WhatsApp.'
        ]
    ];

    // Merge with provided options
    $config = array_merge_recursive($default_config, $options);
    
    // Convert PHP array to JavaScript object
    $js_config = json_encode($config, JSON_PRETTY_PRINT);
    
    // Current site URL for proper API configuration
    $current_url = get_current_url();
    
    // Output the widget HTML and JavaScript
    echo <<<HTML
<!-- ChatGenie Widget for LinkEvolution -->
<script type="text/javascript">
// ChatGenie Configuration
window.ChatGenieConfig = $js_config;

// Load the ChatGenie widget
(function() {
    var script = document.createElement('script');
    script.src = '{$config['apiBaseUrl']}/widget/linkevolution-embed.js';
    script.async = true;
    script.onload = function() {
        console.log('ChatGenie widget loaded successfully for LinkEvolution');
    };
    script.onerror = function() {
        console.error('Failed to load ChatGenie widget');
    };
    document.head.appendChild(script);
})();
</script>

<!-- Preload CSS for better performance -->
<link rel="preconnect" href="{$config['apiBaseUrl']}">

<!-- ChatGenie Analytics (Optional) -->
<script type="text/javascript">
// Track widget engagement
window.ChatGenieAnalytics = {
    trackEvent: function(event, data) {
        // Send analytics to your preferred service
        if (typeof gtag !== 'undefined') {
            gtag('event', event, {
                event_category: 'ChatGenie',
                event_label: 'LinkEvolution',
                custom_map: data
            });
        }
    }
};
</script>

<!-- SEO Meta Tags for Chat Functionality -->
<meta name="description" content="Contacta con LinkEvolution para transformación digital, automatización de procesos y consultoría empresarial en Madrid.">
<meta name="keywords" content="transformación digital, automatización, consultoría, LinkEvolution, chat, soporte">

HTML;
}

function get_current_url() {
    $protocol = isset($_SERVER['HTTPS']) && $_SERVER['HTTPS'] === 'on' ? 'https://' : 'http://';
    $host = $_SERVER['HTTP_HOST'];
    return $protocol . $host;
}

// Auto-render function for easy inclusion
function chatgenie_auto_render() {
    // Check if we should show the widget on this page
    if (should_show_chatgenie()) {
        chatgenie_render_widget();
    }
}

function should_show_chatgenie() {
    // Logic to determine if widget should be shown
    // You can customize this based on your needs
    
    // Don't show on admin pages
    if (strpos($_SERVER['REQUEST_URI'], '/wp-admin/') !== false) {
        return false;
    }
    
    // Don't show on login pages
    if (strpos($_SERVER['REQUEST_URI'], '/login') !== false) {
        return false;
    }
    
    // Show on all other pages by default
    return true;
}

// WordPress integration hooks
if (function_exists('add_action')) {
    // Add to WordPress footer
    add_action('wp_footer', 'chatgenie_auto_render');
}

// Direct call option
if (basename($_SERVER['PHP_SELF']) == 'chatgenie-widget.php') {
    // If this file is called directly, render the widget
    chatgenie_auto_render();
}

/**
 * Advanced Configuration Options
 * 
 * To customize the widget further, you can override the configuration:
 * 
 * chatgenie_render_widget([
 *     'branding' => [
 *         'primaryColor' => '#your-color',
 *         'businessName' => 'Your Business Name'
 *     ],
 *     'position' => 'bottom-left',
 *     'greeting' => 'Custom greeting message'
 * ]);
 * 
 * API Configuration:
 * - Replace 'businessId' with your actual business ID from ChatGenie dashboard
 * - Replace 'apiKey' with your API key
 * - Replace 'apiBaseUrl' with your ChatGenie server URL
 * 
 * Customization Options:
 * - position: 'bottom-right', 'bottom-left', 'top-right', 'top-left'
 * - theme: 'light', 'dark', 'auto'
 * - enableVoice: true/false (voice input functionality)
 * - enableDragging: true/false (allow users to drag the widget)
 * - showQuickActions: true/false (show predefined quick action buttons)
 * 
 * Lead Capture:
 * - Set leadCapture.enabled to true to enable automatic lead generation
 * - Customize leadCapture.triggers with keywords that should trigger lead capture
 * 
 * Business Hours:
 * - Configure businessHours with your actual business schedule
 * - Set timezone to your business timezone
 * - Customize afterHoursMessage for when you're closed
 * 
 * Spanish Localization:
 * - greeting: Welcome message in Spanish
 * - quickActions: Predefined messages in Spanish for digital transformation services
 * - businessHours.afterHoursMessage: After-hours message in Spanish
 */
?>